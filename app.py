import os

from flask import Flask, session, redirect, url_for
from config import Config
from models import db

# Existing models
from models.animal import Animal
from models.production import Production
from models.expense import Expense
from models.income import Income
from models.user import User
from models.health import HealthRecord
from models.labor import Worker, LaborActivity

# Additive models. These create only new tables and never rewrite
# existing farm records.
from models.labor_advance import LaborAdvance
from models.ledger import LedgerAccount, LedgerEntry

# Blueprints
from routes.auth import auth_bp, create_admin
from routes.dashboard import dashboard_bp
from routes.livestock import livestock_bp
from routes.health import health_bp
from routes.labor import labor_bp
from routes.production import production_bp
from routes.expenses import expenses_bp
from routes.finance import finance_bp
from routes.admin import admin_bp
from routes.ai import ai_bp
from routes.ledger import ledger_bp
from routes.reports import reports_bp
from routes.language import language_bp

from services.email_service import mail, send_email


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Keep the local SQLite database directory available.
    os.makedirs(os.path.join(app.root_path, "instance"), exist_ok=True)

    db.init_app(app)
    mail.init_app(app)

    # Main application modules
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(livestock_bp)
    app.register_blueprint(health_bp)
    app.register_blueprint(labor_bp)
    app.register_blueprint(production_bp)
    app.register_blueprint(expenses_bp)
    app.register_blueprint(finance_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(ai_bp)
    app.register_blueprint(ledger_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(language_bp)

    with app.app_context():
        # IMPORTANT: additive only. Existing tables and records are preserved.
        db.create_all()
        create_admin()

        # Default accounts are new records only.
        defaults = [
            ("Cash", "Asset"),
            ("Farm Income", "Income"),
            ("Farm Expenses", "Expense"),
            ("Labor Cost", "Expense"),
            ("Labor Advances", "Asset"),
        ]
        for name, account_type in defaults:
            if not LedgerAccount.query.filter_by(name=name).first():
                db.session.add(
                    LedgerAccount(
                        name=name,
                        account_type=account_type,
                        opening_balance=0,
                    )
                )
        db.session.commit()

    return app


app = create_app()


@app.context_processor
def inject_globals():
    # Available to every template without changing existing routes.
    from datetime import datetime
    from flask import session
    from services.i18n import translate
    language=session.get("language", "en")
    return {"now": datetime.utcnow(), "language": language, "t": lambda text: translate(text, language)}


@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("dashboard.dashboard"))
    return redirect(url_for("auth.login"))


@app.route("/test-email")
def test_email():
    result = send_email(
        subject="Farm Management System - Test Email",
        message="""Hello,

This is a test email from the Farm Management System.

If you received this message, your email notification system is working correctly.

Farm Management System
""",
    )
    if result:
        return "<h2 style='color:green'>Email sent successfully!</h2><p>Check the recipient inbox.</p><a href='/finance/'>Return to Finance</a>"
    return "<h2 style='color:red'>Email failed</h2><p>Check the application logs for the email error.</p><a href='/finance/'>Return to Finance</a>"


if __name__ == "__main__":
    # Render supplies PORT. Locally this remains 5000.
    port = int(os.environ.get("PORT", 5000))
    app.run(
        debug=os.environ.get("FLASK_DEBUG", "1") == "1",
        host="0.0.0.0",
        port=port,
    )
