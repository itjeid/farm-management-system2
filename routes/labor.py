from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db
from models.labor import Worker, LaborActivity
from models.labor_advance import LaborAdvance
from routes.auth import login_required, admin_required
from services.email_service import send_email

labor_bp = Blueprint("labor", __name__, url_prefix="/labor")


def worker_financials(worker):
    activity_total = sum((a.payment or 0) for a in worker.activities)
    # Preserve the existing Worker.salary. Activity amounts are used when
    # activities already define the amount owed; otherwise the salary is the base due.
    total_due = activity_total if activity_total > 0 else (worker.salary or 0)
    advance_total = sum((a.amount or 0) for a in worker.advances)
    remaining = max(total_due - advance_total, 0)
    return total_due, advance_total, remaining


@labor_bp.route("/")
@login_required
def labor():
    workers = Worker.query.order_by(Worker.created_at.desc()).all()
    activities = LaborActivity.query.order_by(LaborActivity.activity_date.desc()).limit(50).all()
    advances = LaborAdvance.query.order_by(LaborAdvance.advance_date.desc()).limit(50).all()

    financials = {}
    for worker in workers:
        financials[worker.id] = worker_financials(worker)

    total_due = sum(v[0] for v in financials.values())
    total_advances = sum(v[1] for v in financials.values())
    total_remaining = sum(v[2] for v in financials.values())

    return render_template(
        "labor.html",
        workers=workers,
        activities=activities,
        advances=advances,
        financials=financials,
        total_due=total_due,
        total_advances=total_advances,
        total_remaining=total_remaining,
    )


@labor_bp.route("/add-worker", methods=["GET", "POST"])
@login_required
def add_worker():
    if request.method == "POST":
        worker_id = (request.form.get("worker_id") or "").strip()
        full_name = (request.form.get("full_name") or "").strip()
        phone = (request.form.get("phone") or "").strip()
        role = (request.form.get("role") or "").strip()
        start_date = request.form.get("start_date")
        status = request.form.get("status") or "Active"
        try:
            salary = float(request.form.get("salary") or 0)
        except (ValueError, TypeError):
            salary = -1

        if not worker_id or not full_name:
            flash("Worker ID and full name are required.", "danger")
            return redirect(url_for("labor.add_worker"))
        if salary < 0:
            flash("Salary cannot be negative.", "danger")
            return redirect(url_for("labor.add_worker"))
        if Worker.query.filter_by(worker_id=worker_id).first():
            flash("Worker ID already exists.", "danger")
            return redirect(url_for("labor.add_worker"))

        date_value = None
        if start_date:
            try:
                date_value = datetime.strptime(start_date, "%Y-%m-%d").date()
            except ValueError:
                flash("Invalid start date.", "danger")
                return redirect(url_for("labor.add_worker"))

        worker = Worker(
            worker_id=worker_id, full_name=full_name, phone=phone,
            role=role, start_date=date_value, salary=salary, status=status
        )
        db.session.add(worker)
        try:
            db.session.commit()
        except Exception as error:
            db.session.rollback()
            print(f"Worker database error: {error}")
            flash("Could not register worker.", "danger")
            return redirect(url_for("labor.add_worker"))

        try:
            send_email(
                subject="New Farm Worker Registered",
                message=f"Worker {worker.full_name} ({worker.worker_id}) was registered. Salary: {worker.salary:,.0f} RWF."
            )
        except Exception as error:
            print(f"Worker email error: {error}")
        flash("Worker successfully registered.", "success")
        return redirect(url_for("labor.labor"))

    return render_template("add_worker.html")


@labor_bp.route("/toggle-status/<int:id>")
@login_required
def toggle_worker_status(id):
    worker = Worker.query.get_or_404(id)
    worker.status = "Inactive" if worker.status == "Active" else "Active"
    try:
        db.session.commit()
        flash(f"{worker.full_name} is now {worker.status}.", "success")
    except Exception as error:
        db.session.rollback()
        print(f"Worker status error: {error}")
        flash("Could not change worker status.", "danger")
    return redirect(url_for("labor.labor"))


@labor_bp.route("/add-activity", methods=["GET", "POST"])
@login_required
def add_activity():
    workers = Worker.query.filter_by(status="Active").order_by(Worker.full_name).all()
    if request.method == "POST":
        try:
            worker = Worker.query.get(int(request.form.get("worker_id")))
            date_value = datetime.strptime(
                request.form.get("activity_date"), "%Y-%m-%d"
            ).date()
            amount = float(request.form.get("amount") or 0)
        except (ValueError, TypeError):
            worker, date_value, amount = None, None, -1

        activity = (request.form.get("activity") or "").strip()
        description = (request.form.get("description") or "").strip()

        if not worker or not date_value or not activity:
            flash("Worker, date and activity are required.", "danger")
            return redirect(url_for("labor.add_activity"))
        if amount < 0:
            flash("Labor amount cannot be negative.", "danger")
            return redirect(url_for("labor.add_activity"))
        if worker.status != "Active":
            flash("Inactive workers cannot receive new activities.", "danger")
            return redirect(url_for("labor.add_activity"))

        record = LaborActivity(
            worker_id=worker.id,
            activity_date=date_value,
            activity=activity,
            # Existing columns are retained for database compatibility.
            hours_worked=0,
            payment=amount,
            description=description,
        )
        db.session.add(record)
        try:
            db.session.commit()
        except Exception as error:
            db.session.rollback()
            print(f"Labor database error: {error}")
            flash("Could not save labor activity.", "danger")
            return redirect(url_for("labor.add_activity"))

        flash("Labor activity recorded successfully.", "success")
        return redirect(url_for("labor.labor"))

    return render_template("add_labor.html", workers=workers)


@labor_bp.route("/add-advance", methods=["GET", "POST"])
@login_required
def add_advance():
    workers = Worker.query.order_by(Worker.full_name).all()
    if request.method == "POST":
        try:
            worker = Worker.query.get(int(request.form.get("worker_id")))
            amount = float(request.form.get("amount") or 0)
            date_value = datetime.strptime(
                request.form.get("advance_date"), "%Y-%m-%d"
            ).date()
        except (ValueError, TypeError):
            worker, amount, date_value = None, 0, None

        notes = (request.form.get("notes") or "").strip()
        if not worker or not date_value or amount <= 0:
            flash("Worker, valid date and positive advance amount are required.", "danger")
            return redirect(url_for("labor.add_advance"))

        due, previous_advances, _ = worker_financials(worker)
        if amount > max(due - previous_advances, 0):
            flash(
                f"Advance cannot exceed the worker's remaining balance ({max(due - previous_advances, 0):,.0f} RWF).",
                "danger",
            )
            return redirect(url_for("labor.add_advance"))

        db.session.add(LaborAdvance(
            worker_id=worker.id, advance_date=date_value,
            amount=amount, notes=notes
        ))
        try:
            db.session.commit()
            flash("Worker advance recorded and remaining salary updated.", "success")
        except Exception as error:
            db.session.rollback()
            print(f"Advance database error: {error}")
            flash("Could not save the advance.", "danger")
        return redirect(url_for("labor.labor"))

    return render_template("add_advance.html", workers=workers)


@labor_bp.route("/delete-advance/<int:id>")
@admin_required
def delete_advance(id):
    advance = LaborAdvance.query.get_or_404(id)
    try:
        db.session.delete(advance)
        db.session.commit()
        flash("Advance deleted successfully.", "success")
    except Exception as error:
        db.session.rollback()
        print(f"Advance deletion error: {error}")
        flash("Could not delete the advance.", "danger")
    return redirect(url_for("labor.labor"))


@labor_bp.route("/delete-activity/<int:id>")
@admin_required
def delete_activity(id):
    activity = LaborActivity.query.get_or_404(id)
    try:
        db.session.delete(activity)
        db.session.commit()
        flash("Labor activity deleted successfully.", "success")
    except Exception as error:
        db.session.rollback()
        print(f"Labor deletion error: {error}")
        flash("Could not delete labor activity.", "danger")
    return redirect(url_for("labor.labor"))
