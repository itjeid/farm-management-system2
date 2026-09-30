from datetime import datetime

from . import db


class Worker(db.Model):

    __tablename__ = "workers"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    worker_id = db.Column(
        db.String(50),
        unique=True,
        nullable=False
    )

    full_name = db.Column(
        db.String(150),
        nullable=False
    )

    phone = db.Column(
        db.String(30)
    )

    role = db.Column(
        db.String(100)
    )

    start_date = db.Column(
        db.Date
    )

    salary = db.Column(
        db.Float,
        default=0
    )

    status = db.Column(
        db.String(30),
        default="Active"
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    activities = db.relationship(
        "LaborActivity",
        backref="worker",
        lazy=True,
        cascade="all, delete-orphan"
    )


class LaborActivity(db.Model):

    __tablename__ = "labor_activities"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    worker_id = db.Column(
        db.Integer,
        db.ForeignKey("workers.id"),
        nullable=False
    )

    activity_date = db.Column(
        db.Date,
        nullable=False
    )

    activity = db.Column(
        db.String(200),
        nullable=False
    )

    hours_worked = db.Column(
        db.Float,
        default=0
    )

    payment = db.Column(
        db.Float,
        default=0
    )

    description = db.Column(
        db.Text
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )