from __future__ import annotations

from typing import Any, cast
from datetime import datetime, timezone

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import NoSuchTableError
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(100), nullable=False)
    score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    predictions: Mapped[list[Prediction]] = cast(Any, relationship(back_populates="user"))

    def __init__(self, username: str, password: str, score: int = 0) -> None:
        self.username = username
        self.password = password
        self.score = score

    def __repr__(self) -> str:
        return f"<User {self.id}: {self.username} {self.score}>"


class Team(db.Model):
    __tablename__ = "team"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    api_team_id: Mapped[int | None] = mapped_column(Integer, unique=True, index=True, nullable=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    tla: Mapped[str | None] = mapped_column(String(10), nullable=True)
    crest_url: Mapped[str | None] = mapped_column(String(255), nullable=True)

    home_fixtures: Mapped[list[Fixture]] = cast(Any, relationship(back_populates="home_team", foreign_keys="Fixture.home_team_id"))
    away_fixtures: Mapped[list[Fixture]] = cast(Any, relationship(back_populates="away_team", foreign_keys="Fixture.away_team_id"))

    def __init__(self, name: str, tla: str | None = None, crest_url: str | None = None, api_team_id: int | None = None) -> None:
        self.name = name
        self.tla = tla
        self.crest_url = crest_url
        self.api_team_id = api_team_id

    def __repr__(self) -> str:
        return f"<Team {self.id}: {self.name}>"

class Fixture(db.Model):
    __tablename__ = "fixture"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    api_fixture_id: Mapped[int | None] = mapped_column(Integer, unique=True, index=True, nullable=True)
    api_league_id: Mapped[int | None] = mapped_column(Integer, index=True, nullable=True)
    api_season: Mapped[int | None] = mapped_column(Integer, index=True, nullable=True)
    api_round: Mapped[str | None] = mapped_column(String(100), nullable=True)
    start_at: Mapped[str | None] = mapped_column(String(40), nullable=True)
    home_team_id: Mapped[int | None] = mapped_column(ForeignKey("team.id"), index=True, nullable=True)
    away_team_id: Mapped[int | None] = mapped_column(ForeignKey("team.id"), index=True, nullable=True)
    home_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    away_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    away_score: Mapped[int | None] = mapped_column(Integer, nullable=True)

    home_team: Mapped[Team] = cast(Any, relationship(back_populates="home_fixtures", foreign_keys="Fixture.home_team_id"))
    away_team: Mapped[Team] = cast(Any, relationship(back_populates="away_fixtures", foreign_keys="Fixture.away_team_id"))
    predictions: Mapped[list[Prediction]] = cast(Any, relationship(back_populates="fixture"))

    def __init__(
        self,
        home_score: int | None = None,
        away_score: int | None = None,
        api_fixture_id: int | None = None,
        api_league_id: int | None = None,
        api_season: int | None = None,
        api_round: str | None = None,
        start_at: str | None = None,
        home_team_id: int | None = None,
        away_team_id: int | None = None,
    ) -> None:
        self.api_fixture_id = api_fixture_id
        self.api_league_id = api_league_id
        self.api_season = api_season
        self.api_round = api_round
        self.start_at = start_at
        self.home_team_id = home_team_id
        self.away_team_id = away_team_id
        self.home_score = home_score
        self.away_score = away_score

    def __repr__(self) -> str:
        hs = "" if self.home_score is None else str(self.home_score)
        as_ = "" if self.away_score is None else str(self.away_score)
        return f"<Fixture {self.id}: {self.home_team_name} {hs}-{as_} {self.away_team_name}>"

    @property
    def home_team_name(self) -> str:
        return self.home_team.name if self.home_team is not None else ""

    @property
    def away_team_name(self) -> str:
        return self.away_team.name if self.away_team is not None else ""

    @property
    def has_started(self) -> bool:
        """Return True when the fixture's `start_at` time is at or before now (server time, UTC).

        The `start_at` column stores an ISO datetime string (UTC, often ending with 'Z').
        This parses that string and compares against the current UTC time.
        If parsing fails or `start_at` is not set, the fixture is considered not started.
        """
        if not self.start_at:
            return False
        try:
            normalized = self.start_at.replace("Z", "+00:00")
            parsed = datetime.fromisoformat(normalized)
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)
            parsed_utc = parsed.astimezone(timezone.utc)
            now_utc = datetime.now(timezone.utc)
            return parsed_utc <= now_utc
        except Exception:
            return False

class Prediction(db.Model):
    __tablename__ = "prediction"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    fixture_id: Mapped[int] = mapped_column(ForeignKey("fixture.id"), nullable=False)
    score1: Mapped[int] = mapped_column(Integer, nullable=False)
    score2: Mapped[int] = mapped_column(Integer, nullable=False)

    user: Mapped[User] = cast(Any, relationship(back_populates="predictions"))
    fixture: Mapped[Fixture] = cast(Any, relationship(back_populates="predictions"))

    def __init__(self, user_id: int, fixture_id: int, score1: int, score2: int) -> None:
        self.user_id = user_id
        self.fixture_id = fixture_id
        self.score1 = score1
        self.score2 = score2

    def __repr__(self) -> str:
        return f"<Prediction {self.id}: ({self.user.username}) {self.fixture.home_team_name} {self.score1}-{self.score2} {self.fixture.away_team_name}>"


def ensure_fixture_schema() -> None:
    from sqlalchemy import inspect, text

    db.create_all()
    try:
        existing_columns = {column["name"] for column in inspect(db.engine).get_columns("fixture")}
    except NoSuchTableError:
        return
    if "kickoff_at" in existing_columns and "start_at" not in existing_columns:
        db.session.execute(text("ALTER TABLE fixture RENAME COLUMN kickoff_at TO start_at"))
        existing_columns.remove("kickoff_at")
        existing_columns.add("start_at")
    column_definitions = {
        "api_fixture_id": "INTEGER",
        "api_league_id": "INTEGER",
        "api_season": "INTEGER",
        "api_round": "VARCHAR(100)",
        "start_at": "VARCHAR(40)",
        "home_team_id": "INTEGER",
        "away_team_id": "INTEGER",
        "home_score": "INTEGER",
        "away_score": "INTEGER",
    }
    altered = False
    for column_name, column_type in column_definitions.items():
        if column_name in existing_columns:
            continue
        db.session.execute(text(f"ALTER TABLE fixture ADD COLUMN {column_name} {column_type}"))
        altered = True
    if altered:
        db.session.commit()

