from datetime import datetime, timedelta, timezone

from src.models import Fixture
from src.tasks import fixtures_due_for_polling
from src.tasks import run_match_poll_cycle


def _create_fixture(db, teams, start_at, home_score=None, away_score=None):
    home_team, away_team, *_ = teams
    fixture = Fixture(
        api_fixture_id=9000 + len(db.session.query(Fixture).all()) + 1,
        api_league_id=1,
        api_season=2026,
        api_round="GROUP_STAGE",
        start_at=start_at,
        home_team_id=home_team.id,
        away_team_id=away_team.id,
        home_score=home_score,
        away_score=away_score,
    )
    db.session.add(fixture)
    db.session.commit()
    return fixture


def test_fixtures_due_for_polling_only_after_two_hours(db, teams):
    now_utc = datetime.now(timezone.utc)
    not_due_fixture = _create_fixture(db, teams, (now_utc - timedelta(hours=1)).isoformat())
    due_fixture = _create_fixture(db, teams, (now_utc - timedelta(hours=3)).isoformat())

    due_fixtures = fixtures_due_for_polling(now_utc)

    assert not_due_fixture not in due_fixtures
    assert due_fixture in due_fixtures


def test_run_match_poll_cycle_updates_scores_when_fixture_returns_score(db, teams, monkeypatch):
    now_utc = datetime.now(timezone.utc)
    fixture = _create_fixture(db, teams, (now_utc - timedelta(hours=3)).isoformat())

    calls = {"update_scores": 0}

    class FakeClient:
        def fetch_fixture(self, api_fixture_id):
            assert api_fixture_id == fixture.api_fixture_id
            from src.api_football import FootballDataFixtureRecord, FootballDataTeamRecord

            home_team = FootballDataTeamRecord(api_team_id=1, name="England", tla="ENG", crest_url=None)
            away_team = FootballDataTeamRecord(api_team_id=2, name="France", tla="FRA", crest_url=None)
            return FootballDataFixtureRecord(
                api_fixture_id=api_fixture_id,
                api_league_id=1,
                api_season=2026,
                api_round="GROUP_STAGE",
                start_at=fixture.start_at,
                is_finished=True,
                home_team=home_team,
                away_team=away_team,
                home_score=2,
                away_score=1,
            )

    def fake_update_scores():
        calls["update_scores"] += 1

    monkeypatch.setattr("src.tasks.FootballDataClient", FakeClient)
    monkeypatch.setattr("src.tasks.update_scores", fake_update_scores)

    result = run_match_poll_cycle(now_utc=now_utc)

    assert result.checked_fixtures == 1
    assert result.polled_fixtures == 1
    assert result.score_changes == 1
    assert calls["update_scores"] == 1


def test_run_match_poll_cycle_does_not_update_scores_when_fixture_not_finished(db, teams, monkeypatch):
    now_utc = datetime.now(timezone.utc)
    fixture = _create_fixture(db, teams, (now_utc - timedelta(hours=2, minutes=5)).isoformat())

    calls = {"update_scores": 0}

    class FakeClient:
        def fetch_fixture(self, api_fixture_id):
            assert api_fixture_id == fixture.api_fixture_id
            from src.api_football import FootballDataFixtureRecord, FootballDataTeamRecord

            home_team = FootballDataTeamRecord(api_team_id=1, name="England", tla="ENG", crest_url=None)
            away_team = FootballDataTeamRecord(api_team_id=2, name="France", tla="FRA", crest_url=None)
            return FootballDataFixtureRecord(
                api_fixture_id=api_fixture_id,
                api_league_id=1,
                api_season=2026,
                api_round="GROUP_STAGE",
                start_at=fixture.start_at,
                is_finished=False,
                home_team=home_team,
                away_team=away_team,
                home_score=2,
                away_score=1,
            )

    def fake_update_scores():
        calls["update_scores"] += 1

    monkeypatch.setattr("src.tasks.FootballDataClient", FakeClient)
    monkeypatch.setattr("src.tasks.update_scores", fake_update_scores)

    result = run_match_poll_cycle(now_utc=now_utc)

    assert result.checked_fixtures == 1
    assert result.polled_fixtures == 1
    assert result.score_changes == 0
    assert calls["update_scores"] == 0