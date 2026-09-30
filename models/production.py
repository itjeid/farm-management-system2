from datetime import datetime
from . import db


class Production(db.Model):
    __tablename__ = "productions"

    id = db.Column(db.Integer, primary_key=True)

    animal_id = db.Column(
        db.Integer,
        db.ForeignKey("animals.id"),
        nullable=False
    )

    production_date = db.Column(
        db.Date,
        nullable=False
    )

    morning_quantity = db.Column(
        db.Float,
        default=0
    )

    evening_quantity = db.Column(
        db.Float,
        default=0
    )

    total_quantity = db.Column(
        db.Float,
        default=0
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    def calculate_total(self):
        self.total_quantity = (
            self.morning_quantity +
            self.evening_quantity
        )