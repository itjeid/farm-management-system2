from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, session
from models import db
from models.animal import Animal
from models.production import Production
from models.expense import Expense
from models.income import Income
from models.health import HealthRecord
from models.labor import Worker, LaborActivity
from models.ledger import LedgerAccount, LedgerEntry
from models.labor_advance import LaborAdvance
from models.user import User
from routes.auth import admin_required

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

MODEL_MAP = {
    "animals": (Animal, ["animal_id", "animal_type", "breed", "gender", "date_of_birth", "health_status", "purchase_price"]),
    "health": (HealthRecord, ["animal_id", "record_date", "health_status", "signs", "vaccination", "medicine_used", "veterinarian", "notes"]),
    "production": (Production, ["animal_id", "production_date", "morning_quantity", "evening_quantity", "total_quantity"]),
    "expenses": (Expense, ["category", "description", "amount", "expense_date"]),
    "income": (Income, ["income_date", "income_type", "description", "quantity", "unit_price", "total_amount", "customer", "notes"]),
    "workers": (Worker, ["worker_id", "full_name", "phone", "role", "start_date", "salary", "status"]),
    "labor": (LaborActivity, ["worker_id", "activity_date", "activity", "payment", "description"]),
    "users": (User, ["username", "role"]),
    "labor_advances": (LaborAdvance, ["worker_id", "advance_date", "amount", "notes"]),
    "ledger_accounts": (LedgerAccount, ["name", "account_type", "opening_balance"]),
    "ledger_entries": (LedgerEntry, ["account_id", "entry_date", "description", "debit", "credit"]),
}

LABELS = {
    "animal_id": "Cow ID", "animal_type": "Animal type", "record_date": "Record date",
    "health_status": "Health status", "medicine_used": "Medicine used",
    "date_of_birth": "Date of birth", "purchase_price": "Purchase price",
    "production_date": "Production date", "morning_quantity": "Morning quantity",
    "evening_quantity": "Evening quantity", "total_quantity": "Total quantity",
    "expense_date": "Expense date", "income_date": "Income date",
    "income_type": "Income type", "total_amount": "Total amount",
    "unit_price": "Unit price", "activity_date": "Activity date",
    "payment": "Labor amount", "worker_id": "Worker", "account_id": "Ledger account", "advance_date": "Advance date",
    "full_name": "Full name", "start_date": "Start date", "role": "Role", "status": "Status",
}


def field_type(model, field):
    typ = getattr(model, field).property.columns[0].type
    name = getattr(typ, "python_type", str).__name__
    if name == "date":
        return "date"
    if name in {"int", "float"}:
        return "number"
    return "text"


@admin_bp.route("/")
@admin_required
def index():
    counts = {
        "Animals": Animal.query.count(), "Health Records": HealthRecord.query.count(),
        "Production": Production.query.count(), "Expenses": Expense.query.count(),
        "Income": Income.query.count(), "Workers": Worker.query.count(),
        "Labor Activities": LaborActivity.query.count(), "Labor Advances": LaborAdvance.query.count(),
        "Ledger Accounts": LedgerAccount.query.count(), "Ledger Entries": LedgerEntry.query.count(),
        "Users": User.query.count(),
    }
    section_counts = {key: model.query.count() for key, (model, _) in MODEL_MAP.items()}
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template("admin.html", counts=counts, section_counts=section_counts,
                           sections=MODEL_MAP, users=users)


@admin_bp.route("/section/<string:section>")
@admin_required
def section(section):
    if section not in MODEL_MAP:
        abort(404)
    model, fields = MODEL_MAP[section]
    records = model.query.order_by(model.id.desc()).limit(200).all()
    return render_template("admin_section.html", section=section, records=records, fields=fields,
                           labels=LABELS, model_name=model.__name__)


@admin_bp.route("/edit/<string:section>/<int:id>", methods=["GET", "POST"])
@admin_required
def edit(section, id):
    if section not in MODEL_MAP:
        abort(404)
    model, editable = MODEL_MAP[section]
    record = model.query.get_or_404(id)

    if request.method == "POST":
        try:
            for field in editable:
                raw = request.form.get(field, "").strip()
                column_type = getattr(model, field).property.columns[0].type
                python_type = getattr(column_type, "python_type", str)
                if python_type.__name__ == "date":
                    value = datetime.strptime(raw, "%Y-%m-%d").date() if raw else None
                elif python_type is int:
                    value = int(raw) if raw else 0
                elif python_type is float:
                    value = float(raw) if raw else 0
                else:
                    value = raw
                if section == "production" and field == "total_quantity":
                    continue
                setattr(record, field, value)

            if section == "animals":
                record.animal_type = "Cow"
            if section == "production":
                record.total_quantity = (record.morning_quantity or 0) + (record.evening_quantity or 0)
            if section == "health":
                animal = Animal.query.get(record.animal_id)
                if animal:
                    animal.health_status = record.health_status

            db.session.commit()
            flash("Record updated successfully. Connected pages now use the updated value.", "success")
            return redirect(url_for("admin.section", section=section))
        except Exception as error:
            db.session.rollback()
            print(f"Admin update error: {error}")
            flash("Could not update the record. Check the values and try again.", "danger")

    fields = []
    workers = Worker.query.order_by(Worker.full_name).all()
    animals = Animal.query.order_by(Animal.animal_id).all()
    ledger_accounts = LedgerAccount.query.order_by(LedgerAccount.name).all()
    for field in editable:
        value = getattr(record, field, "")
        if hasattr(value, "isoformat"):
            value = value.isoformat()
        fields.append({"name": field, "label": LABELS.get(field, field.replace("_", " ").title()),
                       "value": value, "type": field_type(model, field)})
    return render_template("admin_edit.html", section=section, record=record, fields=fields,
                           workers=workers, animals=animals, ledger_accounts=ledger_accounts)


@admin_bp.route("/delete/<string:section>/<int:id>", methods=["POST"])
@admin_required
def delete(section, id):
    if section not in MODEL_MAP:
        abort(404)
    model, _ = MODEL_MAP[section]
    record = model.query.get_or_404(id)

    # Prevent accidental deletion of the currently logged-in admin.
    if section == "users" and record.id == session.get("user_id"):
        flash("You cannot delete your own account while logged in.", "danger")
        return redirect(url_for("admin.section", section=section))

    try:
        db.session.delete(record)
        db.session.commit()
        flash(f"{model.__name__} record deleted successfully.", "success")
    except Exception as error:
        db.session.rollback()
        print(f"Admin deletion error: {error}")
        flash("The record could not be deleted. Check related records first.", "danger")
    return redirect(url_for("admin.section", section=section))


@admin_bp.route("/delete-goats", methods=["POST"])
@admin_required
def delete_goats():
    goats = Animal.query.filter(Animal.animal_type.ilike("goat")).all()
    try:
        count = len(goats)
        for goat in goats:
            db.session.delete(goat)
        db.session.commit()
        flash(f"Removed {count} goat record(s). Cow records were not changed.", "success")
    except Exception as error:
        db.session.rollback()
        print(f"Goat cleanup error: {error}")
        flash("Goat records could not be removed. Check related records.", "danger")
    return redirect(url_for("admin.index"))


@admin_bp.route("/user/<int:id>/access/<action>", methods=["POST"])
@admin_required
def user_access(id, action):
    user = User.query.get_or_404(id)
    if action == "grant":
        user.role = "user"
        message = f"Access granted to {user.username}."
    elif action == "admin":
        user.role = "admin"
        message = f"Administrator access granted to {user.username}."
    elif action == "revoke":
        if user.username == "admin":
            flash("The primary admin account cannot be revoked from this control.", "danger")
            return redirect(url_for("admin.index"))
        user.role = "revoked"
        message = f"Access revoked for {user.username}."
    else:
        abort(400)
    db.session.commit()
    flash(message, "success")
    return redirect(url_for("admin.index"))


@admin_bp.route("/maintenance")
@admin_required
def maintenance():
    return render_template("maintenance.html")
