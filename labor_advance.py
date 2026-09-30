from datetime import datetime
from . import db


class LaborAdvance(db.Model):
    __tablename__ = "labor_advances"

    id = db.Column(db.Integer, primary_key=True)
    worker_id = db.Column(db.Integer, db.ForeignKey("workers.id"), nullable=False)
    advance_date = db.Column(db.Date, nullable=False)
    amount = db.Column(db.Float, nullable=False, default=0)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    worker = db.relationship(
        "Worker",
        backref=db.backref("advances", lazy=True, cascade="all, delete-orphan")
    )
