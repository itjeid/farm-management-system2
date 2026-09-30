from io import BytesIO
from datetime import datetime
from flask import Blueprint, render_template, request, send_file
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import mm
from models.animal import Animal
from models.health import HealthRecord
from models.production import Production
from models.labor import Worker, LaborActivity
from models.labor_advance import LaborAdvance
from models.income import Income
from models.expense import Expense
from models.ledger import LedgerAccount
from routes.auth import login_required
from routes.dashboard import farm_summary

reports_bp = Blueprint("reports", __name__, url_prefix="/reports")
SECTIONS = ["summary", "animals", "health", "production", "labor", "finance", "ledger", "ai"]


def parse_date(value):
    try:
        return datetime.strptime(value, "%Y-%m-%d").date() if value else None
    except ValueError:
        return None


def collect(selected, start_date=None, end_date=None):
    def within(query, field):
        if start_date:
            query = query.filter(field >= start_date)
        if end_date:
            query = query.filter(field <= end_date)
        return query

    out = {"summary": farm_summary()}
    if "animals" in selected:
        out["animals"] = Animal.query.filter(Animal.animal_type.ilike("cow")).order_by(Animal.animal_id).all()
    if "health" in selected:
        out["health"] = within(HealthRecord.query.join(Animal).filter(Animal.animal_type.ilike("cow")), HealthRecord.record_date).order_by(HealthRecord.record_date.desc()).all()
    if "production" in selected:
        out["production"] = within(Production.query.join(Animal).filter(Animal.animal_type.ilike("cow")), Production.production_date).order_by(Production.production_date.desc()).all()
    if "labor" in selected:
        out["labor"] = {
            "workers": Worker.query.order_by(Worker.full_name).all(),
            "activities": within(LaborActivity.query, LaborActivity.activity_date).order_by(LaborActivity.activity_date.desc()).all(),
            "advances": within(LaborAdvance.query, LaborAdvance.advance_date).order_by(LaborAdvance.advance_date.desc()).all(),
        }
    if "finance" in selected:
        out["finance"] = {
            "income": within(Income.query, Income.income_date).order_by(Income.income_date.desc()).all(),
            "expenses": within(Expense.query, Expense.expense_date).order_by(Expense.expense_date.desc()).all(),
        }
    if "ledger" in selected:
        out["ledger"] = LedgerAccount.query.order_by(LedgerAccount.name).all()
    if "ai" in selected:
        out["ai"] = "AI recommendations use current farm records. The AI assistant and cow health scan are available from the Intelligence menu."
    return out


@reports_bp.route("/", methods=["GET", "POST"])
@login_required
def reports():
    selected = request.form.getlist("sections") if request.method == "POST" else SECTIONS
    if not selected:
        selected = ["summary"]
    start_date = parse_date(request.form.get("start_date", "") if request.method == "POST" else request.args.get("start_date", ""))
    end_date = parse_date(request.form.get("end_date", "") if request.method == "POST" else request.args.get("end_date", ""))
    data = collect(selected, start_date, end_date)
    return render_template("reports.html", sections=SECTIONS, selected=selected, data=data,
                           start_date=start_date, end_date=end_date)


@reports_bp.route("/pdf")
@login_required
def report_pdf():
    selected = [x for x in request.args.get("sections", "summary").split(",") if x in SECTIONS] or ["summary"]
    start_date = parse_date(request.args.get("start_date", ""))
    end_date = parse_date(request.args.get("end_date", ""))
    data = collect(selected, start_date, end_date)
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=15*mm, leftMargin=15*mm, topMargin=15*mm, bottomMargin=15*mm)
    styles = getSampleStyleSheet()
    period = f"{start_date or 'All dates'} to {end_date or 'All dates'}"
    story = [Paragraph("FARM MANAGEMENT SYSTEM", styles["Title"]), Paragraph("Management Report", styles["Heading2"]), Paragraph(f"Report period: {period}", styles["BodyText"]), Spacer(1, 8)]
    s = data["summary"]
    story.append(Paragraph(f"Cows: {s['total_animals']} | Income: {s['total_income']:,.0f} RWF | Expenses: {s['total_expenses']:,.0f} RWF | Labor: {s['total_labor']:,.0f} RWF | Net: {s['net_result']:,.0f} RWF", styles["BodyText"]))
    if "animals" in data: story += [Spacer(1,10), Paragraph("Cows", styles["Heading2"]), Table([["ID","Breed","Gender","Health","Registered"]] + [[a.animal_id,a.breed or '-',a.gender or '-',a.health_status or '-',a.created_at.strftime('%Y-%m-%d') if a.created_at else '-'] for a in data["animals"]], repeatRows=1)]
    if "health" in data: story += [Spacer(1,10), Paragraph("Animal Health", styles["Heading2"]), Table([["Date","Cow","Status","Symptoms","Medicine"]] + [[r.record_date,r.animal.animal_id if r.animal else '-',r.health_status,r.signs or '-',r.medicine_used or '-'] for r in data["health"]], repeatRows=1)]
    if "production" in data: story += [Spacer(1,10), Paragraph("Production", styles["Heading2"]), Table([["Date","Cow","Morning","Evening","Total"]] + [[p.production_date,p.animal.animal_id if p.animal else '-',p.morning_quantity,p.evening_quantity,p.total_quantity] for p in data["production"]], repeatRows=1)]
    if "labor" in data:
        story += [Spacer(1,10), Paragraph("Labor & Advances", styles["Heading2"]), Table([["Date","Worker","Activity","Amount"]] + [[a.activity_date,a.worker.full_name if a.worker else '-',a.activity,f"{a.payment or 0:,.0f}"] for a in data["labor"]["activities"]], repeatRows=1)]
        story += [Spacer(1,6), Table([["Date","Worker","Advance"]] + [[a.advance_date,a.worker.full_name if a.worker else '-',f"{a.amount or 0:,.0f}"] for a in data["labor"]["advances"]], repeatRows=1)]
    if "finance" in data: story += [Spacer(1,10), Paragraph("Finance", styles["Heading2"]), Table([["Date","Type","Amount"]] + [[x.income_date,x.income_type,f"+{x.total_amount or 0:,.0f}"] for x in data["finance"]["income"]] + [[x.expense_date,x.category,f"-{x.amount or 0:,.0f}"] for x in data["finance"]["expenses"]], repeatRows=1)]
    if "ledger" in data: story += [Spacer(1,10), Paragraph("Ledger Accounts", styles["Heading2"]), Table([["Account","Type","Opening Balance"]] + [[a.name,a.account_type,f"{a.opening_balance or 0:,.0f}"] for a in data["ledger"]], repeatRows=1)]
    if "ai" in data: story += [Spacer(1,10), Paragraph("AI & Decision Support", styles["Heading2"]), Paragraph(data["ai"], styles["BodyText"])]
    for item in story:
        if isinstance(item, Table):
            item.setStyle(TableStyle([("GRID",(0,0),(-1,-1),0.3,colors.grey),("BACKGROUND",(0,0),(-1,0),colors.HexColor("#e9f5ee")),("FONTSIZE",(0,0),(-1,-1),7),("PADDING",(0,0),(-1,-1),4),("VALIGN",(0,0),(-1,-1),"TOP")]))
    doc.build(story)
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="farm_management_report.pdf", mimetype="application/pdf")
