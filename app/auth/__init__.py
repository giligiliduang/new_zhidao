from flask import Blueprint
auth=Blueprint('auth',__name__)
from . import views

from app.main.forms import SearchForm

@auth.app_context_processor
def inject():

    return dict(searchform=SearchForm())