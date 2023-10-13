from flask import Flask

app = Flask(__name__)

# Load database
from app.components.extract_data import extract_data

from app.controllers import index