from flask import Flask

app = Flask(__name__)

print("Import from app")
# Load database
from app.components.extract_data import extract_data

from app.controllers import index
