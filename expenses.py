from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db
from models.expense import Expense
from routes.auth import login_required

expenses_bp = Blueprint("expenses", __name__, url_prefix="/expenses")

LABOR_CATEGORIES = {"labor", "labour", "salary", "wages", "wage"}


@expenses_bp.route("/")
@login_required
def expenses():
    records = Expense.query.order_by(Expense.expense_date.desc()).all()
    general = [e for e in records if (e.category or "").strip().lower() not in LABOR_CATEGORIES]
    total = sum(e.amount or 0 for e in general)
    return render_template("expenses.html", expenses=general, total_expenses=total)


@expenses_bp.route("/add", methods=["GET", "POST"])
@login_required
def add_expense():
    if request.method == "POST":
        category = (request.form.get("category") or "").strip()
        description = (request.form.get("description") or "").strip()
        try:
            amount = float(request.form.get("amount") or 0)
            date_value = datetime.strptime(
                request.form.get("expense_date"), "%Y-%m-%d"
            ).date()
        except (ValueError, TypeError):
            flash("Enter a valid amount and date.", "danger")
            return redirect(url_for("expenses.add_expense"))

        if not category or amount <= 0:
            flash("Category and a positive amount are required.", "danger")
            return redirect(url_for("expenses.add_expense"))

        if category.lower() in LABOR_CATEGORIES:
            flash("Labor must be recorded in Labor Management. It will appear in Finance as Labor Cost.", "warning")
            return redirect(url_for("expenses.add_expense"))

        db.session.add(Expense(
            category=category,
            description=description,
            amount=amount,
            expense_date=date_value,
        ))
        try:
            db.session.commit()
            flash("Expense recorded successfully.", "success")
        except Exception as error:
            db.session.rollback()
            print(f"Expense database error: {error}")
            flash("Could not save expense.", "danger")
        return redirect(url_for("expenses.expenses"))

    return render_template("add_expense.html")


@expenses_bp.route("/delete/<int:id>")
@login_required
def delete_expense(id):
    record = Expense.query.get_or_404(id)
    try:
        db.session.delete(record)
        db.session.commit()
        flash("Expense deleted successfully.", "success")
    except Exception as error:
        db.session.rollback()
        print(f"Expense deletion error: {error}")
        flash("Could not delete expense.", "danger")
    return redirect(url_for("expenses.expenses"))
