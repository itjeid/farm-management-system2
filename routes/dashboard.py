from flask import Blueprint, render_template
from sqlalchemy import or_
from models import db
from models.animal import Animal
from models.production import Production
from models.expense import Expense
from models.income import Income
from models.health import HealthRecord
from models.labor import Worker, LaborActivity
from models.labor_advance import LaborAdvance
from routes.auth import login_required
from services.ai_service import dashboard_recommendations

dashboard_bp=Blueprint('dashboard',__name__)

def farm_summary():
    labor_categories={'labor','labour','salary','wages','wage'}
    income=float(db.session.query(db.func.coalesce(db.func.sum(Income.total_amount),0)).scalar() or 0)
    expenses=sum((e.amount or 0) for e in Expense.query.all() if (e.category or '').strip().lower() not in labor_categories)
    labor=float(db.session.query(db.func.coalesce(db.func.sum(LaborActivity.payment),0)).scalar() or 0)
    advances=float(db.session.query(db.func.coalesce(db.func.sum(LaborAdvance.amount),0)).scalar() or 0)
    milk=float(db.session.query(db.func.coalesce(db.func.sum(Production.total_quantity),0)).scalar() or 0)
    cows=Animal.query.filter_by(animal_type='Cow')
    sick=cows.filter(or_(Animal.health_status.ilike('%sick%'),Animal.health_status.ilike('%treatment%'))).count()
    treatment=cows.filter(Animal.health_status.ilike('%treatment%')).count()
    return {'total_animals':cows.count(),'total_cows':cows.count(),'total_milk':milk,'total_income':income,'total_expenses':expenses,'total_labor':labor,'total_labor_cost':labor,'total_advances':advances,'net_result':income-expenses-labor,'sick_animals':sick,'under_treatment':treatment,'health_records':HealthRecord.query.count(),'active_workers':Worker.query.filter_by(status='Active').count()}

@dashboard_bp.route('/')
@login_required
def dashboard():
    summary=farm_summary()
    return render_template('dashboard.html',**summary,recommendations=dashboard_recommendations(summary),recent_animals=Animal.query.filter_by(animal_type='Cow').order_by(Animal.created_at.desc()).limit(6).all(),recent_health=HealthRecord.query.join(Animal).filter(Animal.animal_type=='Cow').order_by(HealthRecord.record_date.desc()).limit(6).all(),recent_income=Income.query.order_by(Income.income_date.desc()).limit(6).all(),recent_activities=LaborActivity.query.order_by(LaborActivity.activity_date.desc()).limit(6).all())
