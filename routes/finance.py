from datetime import datetime
from io import BytesIO
from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from models import db
from models.income import Income
from models.expense import Expense
from models.labor import LaborActivity
from models.labor_advance import LaborAdvance
from routes.auth import login_required
from services.email_service import send_email

finance_bp = Blueprint("finance", __name__, url_prefix="/finance")
LABOR_CATEGORIES = {"labor", "labour", "salary", "wages", "wage"}


def financial_data(start=None, end=None):
    iq = Income.query
    eq = Expense.query
    lq = LaborActivity.query
    aq = LaborAdvance.query

    if start:
        iq = iq.filter(Income.income_date >= start)
        eq = eq.filter(Expense.expense_date >= start)
        lq = lq.filter(LaborActivity.activity_date >= start)
        aq = aq.filter(LaborAdvance.advance_date >= start)
    if end:
        iq = iq.filter(Income.income_date <= end)
        eq = eq.filter(Expense.expense_date <= end)
        lq = lq.filter(LaborActivity.activity_date <= end)
        aq = aq.filter(LaborAdvance.advance_date <= end)

    incomes = iq.order_by(Income.income_date.desc()).all()
    all_expenses = eq.order_by(Expense.expense_date.desc()).all()
    expenses = [e for e in all_expenses if (e.category or "").strip().lower() not in LABOR_CATEGORIES]
    labor = lq.order_by(LaborActivity.activity_date.desc()).all()
    advances = aq.order_by(LaborAdvance.advance_date.desc()).all()

    total_income = sum(i.total_amount or 0 for i in incomes)
    total_expenses = sum(e.amount or 0 for e in expenses)
    total_labor = sum(a.payment or 0 for a in labor)
    total_advances = sum(a.amount or 0 for a in advances)
    total_cost = total_expenses + total_labor
    profit = total_income - total_cost

    return locals()


@finance_bp.route("/")
@login_required
def finance():
    start_date = request.args.get("start_date", "").strip()
    end_date = request.args.get("end_date", "").strip()
    start = end = None
    try:
        if start_date:
            start = datetime.strptime(start_date, "%Y-%m-%d").date()
        if end_date:
            end = datetime.strptime(end_date, "%Y-%m-%d").date()
        if start and end and start > end:
            raise ValueError
    except ValueError:
        flash("Please enter a valid date range.", "danger")
        start_date = end_date = ""
        start = end = None

    data = financial_data(start, end)
    return render_template("finance.html", **data, start_date=start_date, end_date=end_date)


@finance_bp.route("/add-income", methods=["GET", "POST"])
@login_required
def add_income():
    if request.method == "POST":
        income_type = (request.form.get("income_type") or "").strip()
        description = (request.form.get("description") or "").strip()
        customer = (request.form.get("customer") or "").strip()
        notes = (request.form.get("notes") or "").strip()
        income_date = (request.form.get("income_date") or "").strip()
        try:
            quantity = float(request.form.get("quantity") or 1)
            unit_price = float(request.form.get("unit_price") or 0)
            date_value = datetime.strptime(income_date, "%Y-%m-%d").date()
        except (ValueError, TypeError):
            flash("Enter valid quantity, price and date.", "danger")
            return redirect(url_for("finance.add_income"))
        if not income_type or quantity <= 0 or unit_price < 0:
            flash("Income type, positive quantity and valid price are required.", "danger")
            return redirect(url_for("finance.add_income"))

        total_amount = quantity * unit_price
        db.session.add(Income(
            income_date=date_value, income_type=income_type,
            description=description, quantity=quantity,
            unit_price=unit_price, total_amount=total_amount,
            customer=customer, notes=notes,
        ))
        try:
            db.session.commit()
            flash("Income recorded successfully.", "success")
        except Exception as error:
            db.session.rollback()
            print(f"Income database error: {error}")
            flash("Could not save income.", "danger")
            return redirect(url_for("finance.add_income"))

        try:
            send_email(
                subject="Farm Income Update",
                message=f"New income recorded: {income_type} — {total_amount:,.0f} RWF."
            )
        except Exception as error:
            print(f"Income email error: {error}")
        return redirect(url_for("finance.finance"))
    return render_template("add_income.html")


@finance_bp.route("/delete-income/<int:id>")
@login_required
def delete_income(id):
    income = Income.query.get_or_404(id)
    try:
        db.session.delete(income)
        db.session.commit()
        flash("Income deleted successfully.", "success")
    except Exception as error:
        db.session.rollback()
        print(f"Income deletion error: {error}")
        flash("Could not delete income.", "danger")
    return redirect(url_for("finance.finance"))


@finance_bp.route("/report")
@login_required
def report():
    start_date = request.args.get("start_date", "")
    end_date = request.args.get("end_date", "")
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d").date() if start_date else None
        end = datetime.strptime(end_date, "%Y-%m-%d").date() if end_date else None
    except ValueError:
        start = end = None
    return render_template("finance_report.html", **financial_data(start, end),
                           start_date=start_date, end_date=end_date)


@finance_bp.route("/report/pdf")
@login_required
def report_pdf():
    data = financial_data()
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.enums import TA_CENTER
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.units import mm

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=15*mm, leftMargin=15*mm,
                                topMargin=15*mm, bottomMargin=15*mm)
        styles = getSampleStyleSheet()
        title = styles["Title"]; title.alignment = TA_CENTER
        story = [Paragraph("FARM MANAGEMENT SYSTEM", title),
                 Paragraph("Comprehensive Financial Report", styles["Heading2"]), Spacer(1, 10)]
        summary = [
            ["Metric", "Amount (RWF)"],
            ["Total Income", f"{data['total_income']:,.0f}"],
            ["General Expenses", f"{data['total_expenses']:,.0f}"],
            ["Labor Cost", f"{data['total_labor']:,.0f}"],
            ["Total Cost", f"{data['total_cost']:,.0f}"],
            ["Net Profit / Loss", f"{data['profit']:,.0f}"],
            ["Labor Advances", f"{data['total_advances']:,.0f}"],
        ]
        table = Table(summary, colWidths=[90*mm, 80*mm])
        table.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#14532d")),
            ("TEXTCOLOR",(0,0),(-1,0),colors.white),
            ("GRID",(0,0),(-1,-1),0.4,colors.grey),
            ("ALIGN",(1,1),(-1,-1),"RIGHT"),
            ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
            ("PADDING",(0,0),(-1,-1),7),
        ]))
        story += [table, Spacer(1, 16), Paragraph("Income and Cost Records", styles["Heading2"])]

        rows = [["Date", "Type", "Description", "Amount (RWF)"]]
        for i in data["incomes"]:
            rows.append([str(i.income_date), i.income_type, i.description or "-", f"{i.total_amount or 0:,.0f}"])
        for e in data["expenses"]:
            rows.append([str(e.expense_date), e.category, e.description or "-", f"-{e.amount or 0:,.0f}"])
        for l in data["labor"]:
            rows.append([str(l.activity_date), "Labor", l.activity, f"-{l.payment or 0:,.0f}"])
        detail = Table(rows, repeatRows=1, colWidths=[27*mm, 38*mm, 75*mm, 30*mm])
        detail.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#e9f5ee")),
            ("GRID",(0,0),(-1,-1),0.3,colors.grey),
            ("VALIGN",(0,0),(-1,-1),"TOP"),
            ("FONTSIZE",(0,0),(-1,-1),8),
            ("PADDING",(0,0),(-1,-1),5),
        ]))
        story += [detail, Spacer(1, 14),
                  Paragraph("This report is generated from the current system records. Existing source records are preserved.", styles["Normal"])]
        doc.build(story)
        buffer.seek(0)
        return send_file(buffer, as_attachment=True, download_name="farm_financial_report.pdf", mimetype="application/pdf")
    except Exception as error:
        print(f"PDF report error: {error}")
        flash("Could not generate PDF report.", "danger")
        return redirect(url_for("finance.finance"))
