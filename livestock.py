from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db
from models.animal import Animal
from routes.auth import login_required, admin_required

livestock_bp=Blueprint('livestock',__name__,url_prefix='/livestock')

@livestock_bp.route('/')
@login_required
def livestock():
    animals=Animal.query.filter_by(animal_type='Cow').order_by(Animal.created_at.desc()).all()
    return render_template('livestock.html',animals=animals)

@livestock_bp.route('/add',methods=['GET','POST'])
@login_required
def add_animal():
    if request.method=='POST':
        animal_id=(request.form.get('animal_id') or '').strip()
        breed=(request.form.get('breed') or '').strip()
        gender=(request.form.get('gender') or '').strip()
        dob_raw=(request.form.get('date_of_birth') or '').strip()
        health=(request.form.get('health_status') or 'Healthy').strip()
        try: price=float(request.form.get('purchase_price') or 0)
        except ValueError: price=-1
        if not animal_id: flash('Cow ID is required.','danger'); return redirect(url_for('livestock.add_animal'))
        if price<0: flash('Purchase price cannot be negative.','danger'); return redirect(url_for('livestock.add_animal'))
        if Animal.query.filter_by(animal_id=animal_id).first(): flash('A cow with this ID already exists.','danger'); return redirect(url_for('livestock.add_animal'))
        dob=None
        if dob_raw:
            try: dob=datetime.strptime(dob_raw,'%Y-%m-%d').date()
            except ValueError: flash('Invalid date of birth.','danger'); return redirect(url_for('livestock.add_animal'))
        db.session.add(Animal(animal_id=animal_id,animal_type='Cow',breed=breed,gender=gender,date_of_birth=dob,health_status=health,purchase_price=price))
        db.session.commit(); flash('Cow successfully registered.','success')
        return redirect(url_for('livestock.livestock'))
    return render_template('add_animal.html')

@livestock_bp.route('/delete/<int:id>')
@admin_required
def delete_animal(id):
    animal=Animal.query.get_or_404(id)
    if animal.animal_type!='Cow': flash('Only cow records are supported by this system.','warning'); return redirect(url_for('livestock.livestock'))
    db.session.delete(animal); db.session.commit(); flash('Cow deleted successfully.','success')
    return redirect(url_for('livestock.livestock'))
