from flask import Blueprint

username = Blueprint('username', __name__)

from . import views
