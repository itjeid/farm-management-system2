from datetime import datetime
from . import db


class LedgerAccount(db.Model):
    __tablename__ = "ledger_accounts"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    account_type = db.Column(db.String(50), nullable=False, default="Asset")
    opening_balance = db.Column(db.Float, nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    entries = db.relationship(
        "LedgerEntry", backref="account", lazy=True,
        cascade="all, delete-orphan"
    )


class LedgerEntry(db.Model):
    __tablename__ = "ledger_entries"

    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey("ledger_accounts.id"), nullable=False)
    entry_date = db.Column(db.Date, nullable=False)
    description = db.Column(db.String(255), nullable=False)
    debit = db.Column(db.Float, nullable=False, default=0)
    credit = db.Column(db.Float, nullable=False, default=0)
    source_type = db.Column(db.String(50))
    source_id = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
