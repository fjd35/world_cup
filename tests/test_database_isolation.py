"""Regression tests for database isolation in tests."""

from src import db as flask_db


def test_testing_environment_uses_an_isolated_database(app_fixture):
    """Ensure tests do not bind to the production sqlite file."""
    with app_fixture.app_context():
        engine_url = str(flask_db.engine.url)
        assert engine_url == "sqlite:///:memory:"
        assert not engine_url.endswith("db.sqlite")
