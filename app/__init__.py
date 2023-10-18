from flask import Flask

app = Flask(__name__)

# Load database
from app.components.basic_dataframes import *

from app.controllers import index
