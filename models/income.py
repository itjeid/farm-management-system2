from datetime import datetime

from models import db


class Income(db.Model):

    __tablename__ = "income"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    income_date = db.Column(
        db.Date,
        nullable=False
    )

    income_type = db.Column(
        db.String(100),
        nullable=False
    )

    description = db.Column(
        db.String(255),
        nullable=True
    )

    quantity = db.Column(
        db.Float,
        nullable=True,
        default=1
    )

    unit_price = db.Column(
        db.Float,
        nullable=True,
        default=0
    )

    total_amount = db.Column(
        db.Float,
        nullable=False,
        default=0
    )

    customer = db.Column(
        db.String(150),
        nullable=True
    )

    notes = db.Column(
        db.Text,
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    def __repr__(self):

        return (
            f"<Income "
            f"{self.income_type} "
            f"{self.total_amount}>"
        )