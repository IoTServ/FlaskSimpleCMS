from flask import Blueprint

mip = Blueprint('mip', __name__)

from . import views