from flask import render_template

from app.main import main


@main.errorhandler(403)
def forbidden(e):
    return render_template('errors/403.html'), 403


@main.errorhandler(404)
def not_found(e):
    return render_template('errors/404.html'), 404


@main.errorhandler(500)
def internal_server_error(e):
    return render_template('errors/500.html'), 500
