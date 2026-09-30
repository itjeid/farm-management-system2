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
from models.animal import Animal
from models.production import Production
from routes.auth import login_required


production_bp = Blueprint(
    "production",
    __name__,
    url_prefix="/production"
)


@production_bp.route("/")
@login_required
def production():

    productions = Production.query.order_by(
        Production.production_date.desc()
    ).all()

    return render_template(
        "production.html",
        productions=productions
    )


@production_bp.route("/add", methods=["GET", "POST"])
@login_required
def add_production():

    animals = Animal.query.filter(
        Animal.animal_type == "Cow"
    ).all()

    if request.method == "POST":

        animal_id = request.form.get(
            "animal_id"
        )

        production_date = request.form.get(
            "production_date"
        )

        morning = float(
            request.form.get(
                "morning_quantity"
            ) or 0
        )

        evening = float(
            request.form.get(
                "evening_quantity"
            ) or 0
        )

        animal = Animal.query.get(
            animal_id
        )

        if not animal:
            flash(
                "Selected animal does not exist.",
                "danger"
            )

            return redirect(
                url_for("production.add_production")
            )

        date_value = datetime.strptime(
            production_date,
            "%Y-%m-%d"
        ).date()

        production = Production(
            animal_id=animal.id,
            production_date=date_value,
            morning_quantity=morning,
            evening_quantity=evening
        )

        production.calculate_total()

        db.session.add(production)
        db.session.commit()

        flash(
            "Production recorded successfully.",
            "success"
        )

        return redirect(
            url_for("production.production")
        )

    return render_template(
        "add_production.html",
        animals=animals
    )