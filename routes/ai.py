import os
from flask import Blueprint, render_template, request, current_app
from werkzeug.utils import secure_filename
from models import db
from models.animal import Animal
from models.production import Production
from models.expense import Expense
from models.income import Income
from models.labor import LaborActivity, Worker
from models.labor_advance import LaborAdvance
from models.health import HealthRecord
from routes.auth import login_required
from services.ai_service import answer_question
from services.disease_ai import analyze_cow

ai_bp = Blueprint('ai', __name__, url_prefix='/ai')


def farm_context():
    labor_categories={'labor','labour','salary','wages','wage'}
    total_income=float(db.session.query(db.func.coalesce(db.func.sum(Income.total_amount),0)).scalar() or 0)
    expenses=Expense.query.all()
    general_expenses=float(sum(e.amount or 0 for e in expenses if (e.category or '').strip().lower() not in labor_categories))
    labor=float(db.session.query(db.func.coalesce(db.func.sum(LaborActivity.payment),0)).scalar() or 0)
    advances=float(db.session.query(db.func.coalesce(db.func.sum(LaborAdvance.amount),0)).scalar() or 0)
    milk=float(db.session.query(db.func.coalesce(db.func.sum(Production.total_quantity),0)).scalar() or 0)
    health=HealthRecord.query.order_by(HealthRecord.record_date.desc()).limit(12).all()
    return {
        'total_animals':Animal.query.filter_by(animal_type='Cow').count(),
        'cows':Animal.query.filter_by(animal_type='Cow').count(),
        'health_records':HealthRecord.query.count(),
        'sick_animals':Animal.query.filter(Animal.animal_type=='Cow', Animal.health_status.ilike('%sick%')).count(),
        'under_treatment':Animal.query.filter(Animal.animal_type=='Cow', Animal.health_status.ilike('%treatment%')).count(),
        'total_milk_litres':milk,'total_income_rwf':total_income,'general_expenses_rwf':general_expenses,
        'labor_cost_rwf':labor,'labor_advances_rwf':advances,'net_result_rwf':total_income-general_expenses-labor,
        'active_workers':Worker.query.filter_by(status='Active').count(),
        'recent_health':[{'animal_id':r.animal.animal_id if r.animal else 'Unknown','status':r.health_status,'date':r.record_date.isoformat(),'medicine':r.medicine_used or '','signs':r.signs or ''} for r in health]
    }

@ai_bp.route('/', methods=['GET','POST'])
@login_required
def assistant():
    question=''; answer=''
    if request.method=='POST':
        question=(request.form.get('question') or '').strip()
        if question:
            answer=answer_question(question, farm_context(), api_key=current_app.config.get('OPENAI_API_KEY'), model=current_app.config.get('OPENAI_MODEL'))
    return render_template('ai_assistant.html', question=question, answer=answer, context=farm_context())

@ai_bp.route('/disease', methods=['GET','POST'])
@login_required
def disease_check():
    result=None
    symptoms=''
    if request.method=='POST':
        symptoms=(request.form.get('symptoms') or '').strip()
        image=request.files.get('image')
        temp_path=None
        try:
            if image and image.filename:
                safe=secure_filename(image.filename)
                upload_dir=os.path.join(current_app.root_path,'instance','ai_uploads')
                os.makedirs(upload_dir, exist_ok=True)
                temp_path=os.path.join(upload_dir,safe)
                image.save(temp_path)
            result=analyze_cow(symptoms,temp_path,current_app.config.get('OPENAI_API_KEY'),current_app.config.get('OPENAI_MODEL','gpt-5.6-luna'))
        finally:
            if temp_path and os.path.exists(temp_path):
                try: os.remove(temp_path)
                except OSError: pass
    return render_template('disease_check.html', result=result, symptoms=symptoms)
