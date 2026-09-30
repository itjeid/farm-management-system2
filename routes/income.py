from datetime import datetime

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from models import db
from models.income import Income

from routes.auth import login_required
from services.email_service import send_email


income_bp = Blueprint(
    "income",
    __name__,
    url_prefix="/income"
)


# ==========================================================
# INCOME PAGE
# ==========================================================

@income_bp.route("/")
@login_required
def income():

    incomes = Income.query.order_by(
        Income.income_date.desc()
    ).all()

    total_income = sum(
        item.total_amount or 0
        for item in incomes
    )

    return render_template(
        "income.html",
        incomes=incomes,
        total_income=total_income
    )


# ==========================================================
# ADD INCOME
# ==========================================================

@income_bp.route(
    "/add",
    methods=["GET", "POST"]
)
@login_required
def add_income():

    if request.method == "POST":

        income_type = (
            request.form.get("income_type")
            or ""
        ).strip()

        description = (
            request.form.get("description")
            or ""
        ).strip()

        customer = (
            request.form.get("customer")
            or ""
        ).strip()

        notes = (
            request.form.get("notes")
            or ""
        ).strip()

        income_date = request.form.get(
            "income_date"
        )

        # --------------------------------------------------
        # QUANTITY
        # --------------------------------------------------

        try:

            quantity = float(
                request.form.get(
                    "quantity"
                ) or 1
            )

        except (ValueError, TypeError):

            quantity = 0

        # --------------------------------------------------
        # UNIT PRICE
        # --------------------------------------------------

        try:

            unit_price = float(
                request.form.get(
                    "unit_price"
                ) or 0
            )

        except (ValueError, TypeError):

            unit_price = 0

        # --------------------------------------------------
        # VALIDATION
        # --------------------------------------------------

        if not income_type:

            flash(
                "Income type is required.",
                "danger"
            )

            return redirect(
                url_for("income.add_income")
            )

        if not income_date:

            flash(
                "Income date is required.",
                "danger"
            )

            return redirect(
                url_for("income.add_income")
            )

        if quantity <= 0:

            flash(
                "Quantity must be greater than zero.",
                "danger"
            )

            return redirect(
                url_for("income.add_income")
            )

        if unit_price < 0:

            flash(
                "Unit price cannot be negative.",
                "danger"
            )

            return redirect(
                url_for("income.add_income")
            )

        # --------------------------------------------------
        # DATE
        # --------------------------------------------------

        try:

            date_value = datetime.strptime(
                income_date,
                "%Y-%m-%d"
            ).date()

        except ValueError:

            flash(
                "Invalid income date.",
                "danger"
            )

            return redirect(
                url_for("income.add_income")
            )

        # --------------------------------------------------
        # CALCULATE TOTAL
        # --------------------------------------------------

        total_amount = (
            quantity *
            unit_price
        )

        # --------------------------------------------------
        # CREATE RECORD
        # --------------------------------------------------

        income = Income(

            income_date=date_value,

            income_type=income_type,

            description=description,

            quantity=quantity,

            unit_price=unit_price,

            total_amount=total_amount,

            customer=customer,

            notes=notes
        )

        db.session.add(income)

        # --------------------------------------------------
        # SAVE
        # --------------------------------------------------

        try:

            db.session.commit()

        except Exception as error:

            db.session.rollback()

            print(
                f"Income database error: {error}"
            )

            flash(
                "Could not save income.",
                "danger"
            )

            return redirect(
                url_for("income.add_income")
            )

        # ==================================================
        # EMAIL ALERT
        # ==================================================

        email_message = f"""
FARM INCOME UPDATE
==================

A new farm income has been recorded.

Income Type:
{income_type}

Date:
{income_date}

Quantity:
{quantity}

Unit Price:
{unit_price:,.0f} RWF

TOTAL INCOME:
{total_amount:,.0f} RWF

Customer:
{customer or "Not provided"}

Description:
{description or "Not provided"}

Notes:
{notes or "Not provided"}

Farm Management System
"""

        email_sent = send_email(

            subject="Farm Income Update",

            message=email_message
        )

        if email_sent:

            print(
                "Income notification email sent successfully."
            )

        else:

            print(
                "Income notification email was not sent."
            )

        flash(
            "Income recorded successfully.",
            "success"
        )

        return redirect(
            url_for("finance.finance")
        )

    return render_template(
        "add_income.html"
    )


# ==========================================================
# DELETE INCOME
# ==========================================================

@income_bp.route(
    "/delete/<int:id>"
)
@login_required
def delete_income(id):

    income = Income.query.get_or_404(id)

    try:

        db.session.delete(
            income
        )

        db.session.commit()

        flash(
            "Income deleted successfully.",
            "success"
        )

    except Exception as error:

        db.session.rollback()

        print(
            f"Income deletion error: {error}"
        )

        flash(
            "Could not delete income.",
            "danger"
        )

    return redirect(
        url_for("finance.finance")
    )