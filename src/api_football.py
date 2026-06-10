from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from flask import current_app
from sqlalchemy import or_

from . import db
from .models import Prediction
from .models import Fixture
from .models import Team


@dataclass(frozen=True)
class FootballDataCompetition:
    id: str
    code: str | None
    name: str
    country: str | None
    current_season: int | None


@dataclass(frozen=True)
class FootballDataFixtureRecord:
    api_fixture_id: int
    api_league_id: int | None
    api_season: int | None
    api_round: str | None
    start_at: str | None
    home_team: FootballDataTeamRecord
    away_team: FootballDataTeamRecord
    home_score: int | None
    away_score: int | None


@dataclass(frozen=True)
class FootballDataTeamRecord:
    api_team_id: int | None
    name: str
    tla: str | None
    crest_url: str | None


@dataclass(frozen=True)
class FixtureSyncResult:
    competition_id: str
    competition_name: str
    season: int
    inserted: int
    updated: int
    fetched: int


class FootballDataError(RuntimeError):
    pass


class FootballDataClient:
    def __init__(self) -> None:
        self.base_url = current_app.config.get("FOOTBALL_DATA_BASE_URL", "https://api.football-data.org/v4").rstrip("/")
        self.api_token = current_app.config.get("FOOTBALL_DATA_TOKEN", "")
        self.token_header = current_app.config.get("FOOTBALL_DATA_TOKEN_HEADER", "X-Auth-Token")
        self.timeout = float(current_app.config.get("FOOTBALL_DATA_TIMEOUT", 20))

    def _request(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        if not self.api_token:
            raise FootballDataError("football-data.org token is not configured")
        query = f"?{urlencode(params)}" if params else ""
        url = f"{self.base_url}{path}{query}"
        request = Request(url, headers={self.token_header: str(self.api_token)})
        try:
            with urlopen(request, timeout=self.timeout) as response:
                payload = response.read().decode("utf-8")
        except HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise FootballDataError(f"football-data.org request failed ({exc.code}): {body}") from exc
        except URLError as exc:
            raise FootballDataError(f"football-data.org request failed: {exc.reason}") from exc
        return _json_loads(payload)

    def resolve_competition(self, code: str = "WC") -> FootballDataCompetition:
        payload = self._request(f"/competitions/{code}")
        return _parse_competition(payload)

    def fetch_fixtures(self, competition_code: str, season: int) -> list[FootballDataFixtureRecord]:
        payload = self._request(f"/competitions/{competition_code}/matches", {"season": season})
        return [_parse_fixture(item) for item in payload.get("matches", [])]


def sync_world_cup_fixtures(season: int = 2026, competition_code: str = "WC") -> FixtureSyncResult:
    client = FootballDataClient()
    competition = client.resolve_competition(competition_code)
    records = client.fetch_fixtures(competition.code or competition_code, season)
    imported_ids = {record.api_fixture_id for record in records if record.api_fixture_id is not None}
    now_utc = datetime.now(timezone.utc)
    inserted = 0
    updated = 0
    for record in records:
        home_team = _upsert_team(record.home_team)
        away_team = _upsert_team(record.away_team)
        start_at = _parse_utc_datetime(record.start_at)
        fixture = db.session.query(Fixture).filter_by(api_fixture_id=record.api_fixture_id).first()
        if fixture is None:
            fixture = Fixture(
                home_score=record.home_score,
                away_score=record.away_score,
                api_fixture_id=record.api_fixture_id,
                api_league_id=record.api_league_id,
                api_season=record.api_season,
                api_round=record.api_round,
                start_at=record.start_at,
                home_team_id=home_team.id if home_team is not None else None,
                away_team_id=away_team.id if away_team is not None else None,
            )
            db.session.add(fixture)
            inserted += 1
        else:
            fixture.home_score = record.home_score
            fixture.away_score = record.away_score
            fixture.api_league_id = record.api_league_id
            fixture.api_season = record.api_season
            fixture.api_round = record.api_round
            fixture.start_at = record.start_at
            fixture.home_team_id = home_team.id if home_team is not None else None
            fixture.away_team_id = away_team.id if away_team is not None else None
            updated += 1
    if imported_ids:
        orphaned_fixtures = db.session.query(Fixture).filter(
            or_(Fixture.api_fixture_id.is_(None), ~Fixture.api_fixture_id.in_(imported_ids))
        ).all()
    else:
        orphaned_fixtures = db.session.query(Fixture).all()
    orphaned_ids = [fixture.id for fixture in orphaned_fixtures]
    if orphaned_ids:
        db.session.query(Prediction).filter(Prediction.fixture_id.in_(orphaned_ids)).delete(synchronize_session=False)
        for fixture in orphaned_fixtures:
            db.session.delete(fixture)
    db.session.commit()
    return FixtureSyncResult(
        competition_id=competition.id,
        competition_name=competition.name,
        season=season,
        inserted=inserted,
        updated=updated,
        fetched=len(records),
    )


def _parse_competition(payload: dict[str, Any]) -> FootballDataCompetition:
    return FootballDataCompetition(
        id=str(payload.get("id")),
        code=_string_or_none(payload.get("code")),
        name=_string_or_empty(payload.get("name")),
        country=_country_name(payload.get("area")),
        current_season=_current_season(payload.get("currentSeason")),
    )


def _parse_fixture(match: dict[str, Any]) -> FootballDataFixtureRecord:
    competition = match.get("competition", {})
    season = match.get("season", {})
    score = match.get("score", {})
    home_team = match.get("homeTeam", {})
    away_team = match.get("awayTeam", {})
    return FootballDataFixtureRecord(
        api_fixture_id=_int_or_none(match.get("id")) or 0,
        api_league_id=_int_or_none(competition.get("id")),
        api_season=_int_or_none(season.get("startDate", "")[:4]) or season.get("id"),
        api_round=_string_or_none(match.get("stage")) or _string_or_none(match.get("group")),
        start_at=_string_or_none(match.get("utcDate")),
        home_team=_parse_team(home_team),
        away_team=_parse_team(away_team),
        home_score=_int_or_none((score.get("fullTime") or {}).get("home")),
        away_score=_int_or_none((score.get("fullTime") or {}).get("away")),
    )

def _parse_team(team: dict[str, Any]) -> FootballDataTeamRecord:
    return FootballDataTeamRecord(
        api_team_id=_int_or_none(team.get("id")),
        name=_string_or_empty(team.get("name")),
        tla=_string_or_none(team.get("tla")),
        crest_url=_string_or_none(team.get("crest")) or _string_or_none(team.get("crestUrl")),
    )

def _upsert_team(team_record: FootballDataTeamRecord) -> Team | None:
    if team_record.api_team_id is None and not team_record.name:
        return None

    team = None
    if team_record.api_team_id is not None:
        team = db.session.query(Team).filter_by(api_team_id=team_record.api_team_id).first()
    if team is None and team_record.name:
        team = db.session.query(Team).filter_by(name=team_record.name).first()
    if team is None:
        team = Team(
            name=team_record.name,
            tla=team_record.tla,
            crest_url=team_record.crest_url,
            api_team_id=team_record.api_team_id,
        )
        db.session.add(team)
        db.session.flush()
        return team
    team.name = team_record.name
    team.tla = team_record.tla
    team.crest_url = team_record.crest_url
    team.api_team_id = team_record.api_team_id
    db.session.flush()
    return team


def _current_season(current_season: Any) -> int | None:
    if not isinstance(current_season, dict):
        return None
    return _int_or_none(str(current_season.get("startDate", ""))[:4])


def _country_name(area: Any) -> str | None:
    if not isinstance(area, dict):
        return None
    return _string_or_none(area.get("name"))


def _json_loads(payload: str) -> dict[str, Any]:
    import json

    return json.loads(payload)


def _int_or_none(value: Any) -> int | None:
    if value is None or value == "":
        return None
    return int(value)


def _string_or_none(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value)
    return text if text else None


def _string_or_empty(value: Any) -> str:
    return _string_or_none(value) or ""


def _parse_utc_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    normalized = value.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)