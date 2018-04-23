from flask import Blueprint, request
from libraries.JsonApi import *

api = Blueprint('api', __name__, url_prefix='/api')

from . import index
from . import search
