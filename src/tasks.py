from __future__ import annotations

import threading
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from .api_football import FootballDataClient, FootballDataError, upsert_fixture_from_record
from .models import Fixture, db
from .main import update_scores

MATCH_POLL_DELAY = timedelta(hours=2)
MATCH_POLL_INTERVAL_SECONDS = 60

_poll_thread: threading.Thread | None = None
_poll_thread_lock = threading.Lock()
_poll_stop_event = threading.Event()


@dataclass(frozen=True)
class MatchPollCycleResult:
    checked_fixtures: int
    polled_fixtures: int
    score_changes: int


def fixture_poll_ready_at(fixture: Fixture) -> datetime | None:
    start_at = _parse_utc_datetime(fixture.start_at)
    if start_at is None:
        return None
    return start_at + MATCH_POLL_DELAY


def fixture_should_poll(fixture: Fixture, now_utc: datetime | None = None) -> bool:
    if fixture.home_score is not None and fixture.away_score is not None:
        return False
    ready_at = fixture_poll_ready_at(fixture)
    if ready_at is None:
        return False
    now = now_utc or datetime.now(timezone.utc)
    return now >= ready_at


def fixtures_due_for_polling(now_utc: datetime | None = None) -> list[Fixture]:
    candidates = (
        db.session.query(Fixture)
        .filter(Fixture.start_at.isnot(None), Fixture.home_score.is_(None), Fixture.away_score.is_(None))
        .order_by(Fixture.start_at, Fixture.id)
        .all()
    )
    now = now_utc or datetime.now(timezone.utc)
    return [fixture for fixture in candidates if fixture_should_poll(fixture, now)]


def run_match_poll_cycle(
    *,
    season: int = 2026,
    competition_code: str = "WC",
    now_utc: datetime | None = None,
) -> MatchPollCycleResult:
    due_fixtures = fixtures_due_for_polling(now_utc)
    if not due_fixtures:
        return MatchPollCycleResult(checked_fixtures=0, polled_fixtures=0, score_changes=0)

    score_changes = 0
    client = FootballDataClient()
    for fixture in due_fixtures:
        if fixture.api_fixture_id is None:
            continue
        try:
            record = client.fetch_fixture(fixture.api_fixture_id)
        except FootballDataError:
            raise
        if record.is_finished:
            _, _, fixture_score_changed = upsert_fixture_from_record(record)
            if fixture_score_changed:
                score_changes += 1

    if score_changes > 0:
        update_scores()

    return MatchPollCycleResult(
        checked_fixtures=len(due_fixtures),
        polled_fixtures=len(due_fixtures),
        score_changes=score_changes,
    )


def start_match_polling_scheduler(app) -> None:
    if app.config.get("TESTING"):
        return

    with _poll_thread_lock:
        global _poll_thread
        if _poll_thread is not None and _poll_thread.is_alive():
            return

        interval_seconds = int(app.config.get("MATCH_POLL_INTERVAL_SECONDS", MATCH_POLL_INTERVAL_SECONDS))
        competition_code = str(app.config.get("MATCH_POLLING_COMPETITION_CODE", "WC"))
        season = int(app.config.get("MATCH_POLLING_SEASON", 2026))

        def _loop() -> None:
            while not _poll_stop_event.wait(interval_seconds):
                with app.app_context():
                    try:
                        run_match_poll_cycle(season=season, competition_code=competition_code)
                    except FootballDataError as exc:
                        app.logger.warning("Match polling failed: %s", exc)

        _poll_thread = threading.Thread(target=_loop, name="match-poll-scheduler", daemon=True)
        _poll_thread.start()
        app.logger.info(
            "Started match polling scheduler for %s season %s every %s seconds",
            competition_code,
            season,
            interval_seconds,
        )


def stop_match_polling_scheduler() -> None:
    _poll_stop_event.set()


def _parse_utc_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    normalized = value.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)