from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from models import db
from models.ledger import LedgerAccount, LedgerEntry
from models.income import Income
from models.expense import Expense
from models.labor import LaborActivity
from models.labor_advance import LaborAdvance
from routes.auth import login_required, admin_required

ledger_bp = Blueprint("ledger", __name__, url_prefix="/ledger")
LABOR_CATEGORIES = {"labor", "labour", "salary", "wages", "wage"}


def source_transactions():
    rows = []

    for x in Income.query.order_by(Income.income_date, Income.id).all():
        rows += [
            {"date": x.income_date, "description": f"Income: {x.income_type}",
             "account": "Cash", "debit": x.total_amount or 0, "credit": 0,
             "source": "Income", "source_id": x.id},
            {"date": x.income_date, "description": f"Income: {x.income_type}",
             "account": "Farm Income", "debit": 0, "credit": x.total_amount or 0,
             "source": "Income", "source_id": x.id},
        ]

    for x in Expense.query.order_by(Expense.expense_date, Expense.id).all():
        if (x.category or "").strip().lower() in LABOR_CATEGORIES:
            continue
        rows += [
            {"date": x.expense_date, "description": f"Expense: {x.category}",
             "account": "Farm Expenses", "debit": x.amount or 0, "credit": 0,
             "source": "Expense", "source_id": x.id},
            {"date": x.expense_date, "description": f"Expense: {x.category}",
             "account": "Cash", "debit": 0, "credit": x.amount or 0,
             "source": "Expense", "source_id": x.id},
        ]

    for x in LaborActivity.query.order_by(LaborActivity.activity_date, LaborActivity.id).all():
        amount = x.payment or 0
        rows += [
            {"date": x.activity_date, "description": f"Labor: {x.activity}",
             "account": "Labor Cost", "debit": amount, "credit": 0,
             "source": "Labor", "source_id": x.id},
            {"date": x.activity_date, "description": f"Labor: {x.activity}",
             "account": "Cash", "debit": 0, "credit": amount,
             "source": "Labor", "source_id": x.id},
        ]

    for x in LaborAdvance.query.order_by(LaborAdvance.advance_date, LaborAdvance.id).all():
        amount = x.amount or 0
        rows += [
            {"date": x.advance_date, "description": "Worker advance",
             "account": "Labor Advances", "debit": amount, "credit": 0,
             "source": "Labor Advance", "source_id": x.id},
            {"date": x.advance_date, "description": "Worker advance",
             "account": "Cash", "debit": 0, "credit": amount,
             "source": "Labor Advance", "source_id": x.id},
        ]

    for x in LedgerEntry.query.order_by(LedgerEntry.entry_date, LedgerEntry.id).all():
        rows.append({
            "date": x.entry_date, "description": x.description,
            "account": x.account.name if x.account else "Unknown",
            "debit": x.debit or 0, "credit": x.credit or 0,
            "source": "Manual", "source_id": x.id,
        })

    return sorted(rows, key=lambda r: (r["date"], r["source"], r["source_id"]))


def account_balances():
    accounts = LedgerAccount.query.order_by(LedgerAccount.name).all()
    tx = source_transactions()
    result = []

    for account in accounts:
        debit = sum(r["debit"] for r in tx if r["account"] == account.name)
        credit = sum(r["credit"] for r in tx if r["account"] == account.name)
        normal_debit = account.account_type in {"Asset", "Expense"}
        closing = (account.opening_balance + debit - credit) if normal_debit else (
            account.opening_balance + credit - debit
        )
        result.append({
            "account": account,
            "debit": debit,
            "credit": credit,
            "closing": closing,
        })
    return result


@ledger_bp.route("/")
@login_required
def ledger():
    return render_template(
        "ledger.html",
        rows=account_balances(),
        transactions=source_transactions(),
    )


@ledger_bp.route("/account/<int:account_id>")
@login_required
def account_detail(account_id):
    account = LedgerAccount.query.get_or_404(account_id)
    transactions = [r for r in source_transactions() if r["account"] == account.name]
    debit = sum(r["debit"] for r in transactions)
    credit = sum(r["credit"] for r in transactions)
    normal_debit = account.account_type in {"Asset", "Expense"}
    closing = (account.opening_balance + debit - credit) if normal_debit else (
        account.opening_balance + credit - debit
    )
    return render_template(
        "ledger_account.html", account=account, transactions=transactions,
        debit=debit, credit=credit, closing=closing
    )


@ledger_bp.route("/accounts/add", methods=["POST"])
@admin_required
def add_account():
    name = (request.form.get("name") or "").strip()
    account_type = (request.form.get("account_type") or "Asset").strip()
    try:
        opening = float(request.form.get("opening_balance") or 0)
    except (ValueError, TypeError):
        opening = 0
    if not name:
        flash("Account name is required.", "danger")
        return redirect(url_for("ledger.ledger"))
    if LedgerAccount.query.filter_by(name=name).first():
        flash("That account already exists.", "danger")
        return redirect(url_for("ledger.ledger"))
    db.session.add(LedgerAccount(name=name, account_type=account_type, opening_balance=opening))
    try:
        db.session.commit()
        flash("Ledger account created successfully.", "success")
    except Exception as error:
        db.session.rollback()
        print(f"Ledger account error: {error}")
        flash("Could not create account.", "danger")
    return redirect(url_for("ledger.ledger"))


@ledger_bp.route("/entry/add", methods=["GET", "POST"])
@admin_required
def add_entry():
    accounts = LedgerAccount.query.order_by(LedgerAccount.name).all()
    if request.method == "POST":
        try:
            account = LedgerAccount.query.get(int(request.form.get("account_id")))
            date_value = datetime.strptime(request.form.get("entry_date"), "%Y-%m-%d").date()
            debit = float(request.form.get("debit") or 0)
            credit = float(request.form.get("credit") or 0)
        except (ValueError, TypeError):
            account, date_value, debit, credit = None, None, 0, 0

        description = (request.form.get("description") or "").strip()
        if not account or not date_value or not description or debit < 0 or credit < 0 or (debit == 0 and credit == 0):
            flash("Account, date, description and a debit or credit amount are required.", "danger")
            return redirect(url_for("ledger.add_entry"))
        if debit and credit:
            flash("Use either Debit or Credit for one ledger line.", "danger")
            return redirect(url_for("ledger.add_entry"))

        db.session.add(LedgerEntry(
            account_id=account.id, entry_date=date_value,
            description=description, debit=debit, credit=credit,
            source_type="manual",
        ))
        try:
            db.session.commit()
            flash("Ledger transaction recorded successfully.", "success")
        except Exception as error:
            db.session.rollback()
            print(f"Ledger entry error: {error}")
            flash("Could not save ledger transaction.", "danger")
        return redirect(url_for("ledger.ledger"))

    return render_template("ledger_entry.html", accounts=accounts)
