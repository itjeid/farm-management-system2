from datetime import datetime
from . import db


class Animal(db.Model):
    __tablename__ = "animals"

    id = db.Column(db.Integer, primary_key=True)

    animal_id = db.Column(db.String(50), unique=True, nullable=False)

    animal_type = db.Column(db.String(20), nullable=False)

    breed = db.Column(db.String(100))

    gender = db.Column(db.String(20))

    date_of_birth = db.Column(db.Date)

    health_status = db.Column(
        db.String(100),
        default="Healthy"
    )

    purchase_price = db.Column(
        db.Float,
        default=0
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    productions = db.relationship(
        "Production",
        backref="animal",
        lazy=True,
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Animal {self.animal_id}>"