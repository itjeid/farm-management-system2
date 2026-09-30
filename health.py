from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db
from models.animal import Animal
from models.health import HealthRecord
from routes.auth import login_required, admin_required
from services.email_service import send_email

health_bp=Blueprint('health',__name__,url_prefix='/health')

@health_bp.route('/')
@login_required
def health():
    records=HealthRecord.query.join(Animal).filter(Animal.animal_type=='Cow').order_by(HealthRecord.record_date.desc()).all()
    cows=Animal.query.filter_by(animal_type='Cow').all()
    return render_template('health.html',records=records,cows=cows)

@health_bp.route('/add',methods=['GET','POST'])
@login_required
def add_health():
    animals=Animal.query.filter_by(animal_type='Cow').order_by(Animal.animal_id).all()
    if request.method=='POST':
        try: animal=Animal.query.filter_by(id=int(request.form.get('animal_id')),animal_type='Cow').first()
        except (ValueError,TypeError): animal=None
        try: date_value=datetime.strptime(request.form.get('record_date',''),'%Y-%m-%d').date()
        except ValueError: date_value=None
        status=(request.form.get('health_status') or 'Healthy').strip()
        if not animal or not date_value: flash('Select a cow and enter a valid date.','danger'); return redirect(url_for('health.add_health'))
        record=HealthRecord(animal_id=animal.id,record_date=date_value,health_status=status,signs=request.form.get('signs'),vaccination=request.form.get('vaccination'),medicine_used=request.form.get('medicine_used'),veterinarian=request.form.get('veterinarian'),notes=request.form.get('notes'))
        db.session.add(record); animal.health_status=status
        try: db.session.commit()
        except Exception as error: db.session.rollback(); print(error); flash('Could not save the health record.','danger'); return redirect(url_for('health.add_health'))
        if status in {'Sick','Under Treatment'}:
            send_email(subject='Farm Health Alert',message=f'Cow {animal.animal_id} is {status}. Symptoms: {record.signs or "Not provided"}.')
        flash('Cow health record saved successfully.','success'); return redirect(url_for('health.health'))
    return render_template('add_health.html',animals=animals)

@health_bp.route('/edit/<int:id>',methods=['GET','POST'])
@admin_required
def edit_health(id):
    record=HealthRecord.query.get_or_404(id); animals=Animal.query.filter_by(animal_type='Cow').order_by(Animal.animal_id).all()
    if request.method=='POST':
        try: animal=Animal.query.filter_by(id=int(request.form.get('animal_id')),animal_type='Cow').first(); date_value=datetime.strptime(request.form.get('record_date',''),'%Y-%m-%d').date()
        except (ValueError,TypeError): animal=None; date_value=None
        if not animal or not date_value: flash('Invalid cow or date.','danger'); return redirect(url_for('health.edit_health',id=id))
        record.animal_id=animal.id; record.record_date=date_value; record.health_status=(request.form.get('health_status') or 'Healthy').strip(); record.signs=request.form.get('signs'); record.vaccination=request.form.get('vaccination'); record.medicine_used=request.form.get('medicine_used'); record.veterinarian=request.form.get('veterinarian'); record.notes=request.form.get('notes'); animal.health_status=record.health_status
        try: db.session.commit(); flash('Health and treatment record updated.','success'); return redirect(url_for('health.health'))
        except Exception as error: db.session.rollback(); print(error); flash('Could not update the health record.','danger')
    return render_template('edit_health.html',record=record,animals=animals)

@health_bp.route('/delete/<int:id>')
@admin_required
def delete_health(id):
    record=HealthRecord.query.get_or_404(id); db.session.delete(record); db.session.commit(); flash('Health record deleted.','success'); return redirect(url_for('health.health'))
