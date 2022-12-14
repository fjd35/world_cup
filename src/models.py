from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    score = db.Column(db.Integer, nullable=False, default=0)

    predictions = db.relationship("Prediction", back_populates="user")

    def __repr__(self):
        return f"<User {self.id}: {self.username} {self.score}>"

class Fixture(db.Model):
    __tablename__ = "fixture"
    id = db.Column(db.Integer, primary_key=True)
    team1 = db.Column(db.String(100), nullable=False)
    team2 = db.Column(db.String(100), nullable=False)
    is_finished = db.Column(db.Boolean, nullable=False, default=False)
    score1 = db.Column(db.Integer, nullable=True)
    score2 = db.Column(db.Integer, nullable=True)

    predictions = db.relationship("Prediction", back_populates="fixture")

    def __repr__(self):
        return f"<Fixture {self.id}: {self.team1} {self.score1}-{self.score2} {self.team2}>"

class Prediction(db.Model):
    __tablename__ = "prediction"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    fixture_id = db.Column(db.Integer, db.ForeignKey("fixture.id"), nullable=False)
    score1 = db.Column(db.Integer, nullable=False)
    score2 = db.Column(db.Integer, nullable=False)

    user = db.relationship("User", back_populates="predictions")
    fixture = db.relationship("Fixture", back_populates="predictions")

    def __repr__(self):
        return f"<Prediction {self.id}: ({self.user.username}) {self.fixture.team1} {self.score1}-{self.score2} {self.fixture.team2}>"

