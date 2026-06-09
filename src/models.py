from __future__ import annotations

from typing import Any, cast

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Boolean, ForeignKey, Integer, String
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

class Fixture(db.Model):
    __tablename__ = "fixture"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    team1: Mapped[str] = mapped_column(String(100), nullable=False)
    team2: Mapped[str] = mapped_column(String(100), nullable=False)
    is_finished: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    score1: Mapped[int | None] = mapped_column(Integer, nullable=True)
    score2: Mapped[int | None] = mapped_column(Integer, nullable=True)

    predictions: Mapped[list[Prediction]] = cast(Any, relationship(back_populates="fixture"))

    def __init__(
        self,
        team1: str,
        team2: str,
        is_finished: bool = False,
        score1: int | None = None,
        score2: int | None = None,
    ) -> None:
        self.team1 = team1
        self.team2 = team2
        self.is_finished = is_finished
        self.score1 = score1
        self.score2 = score2

    def __repr__(self) -> str:
        return f"<Fixture {self.id}: {self.team1} {self.score1}-{self.score2} {self.team2}>"

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
        return f"<Prediction {self.id}: ({self.user.username}) {self.fixture.team1} {self.score1}-{self.score2} {self.fixture.team2}>"

