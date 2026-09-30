from flask import Blueprint, session, redirect, request, url_for
language_bp=Blueprint('language',__name__)
@language_bp.route('/language/<lang>')
def change_language(lang):
    session['language']='rw' if lang=='rw' else 'en'
    return redirect(request.referrer or url_for('dashboard.dashboard'))
