from datetime import datetime

from . import db


class HealthRecord(db.Model):

    __tablename__ = "health_records"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    animal_id = db.Column(
        db.Integer,
        db.ForeignKey("animals.id"),
        nullable=False
    )

    record_date = db.Column(
        db.Date,
        nullable=False
    )

    health_status = db.Column(
        db.String(50),
        nullable=False
    )

    signs = db.Column(
        db.Text
    )

    vaccination = db.Column(
        db.String(150)
    )

    medicine_used = db.Column(
        db.String(150)
    )

    veterinarian = db.Column(
        db.String(150)
    )

    notes = db.Column(
        db.Text
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    animal = db.relationship(
        "Animal",
        backref=db.backref(
            "health_records",
            lazy=True
        )
    )

    def __repr__(self):

        return (
            f"<HealthRecord {self.id}>"
        )