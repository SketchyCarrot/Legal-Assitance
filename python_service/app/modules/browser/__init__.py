from flask import Blueprint

bp = Blueprint('browser', __name__)

from . import routes 