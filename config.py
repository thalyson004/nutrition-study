import os
from datetime import timedelta

from dotenv import load_dotenv

load_dotenv()

# --------------------------------------------------------------------------------------------------#

DEBUG = True

# --------------------------------------------------------------------------------------------------#

# default = 'postgresql://postgres:admin@localhost:5432/postgres_db'

#SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI', default)
SQLALCHEMY_DATABASE_URI = default
DEFAULT_DATE_FORMAT = "%d/%m/%Y"
SQLALCHEMY_TRACK_MODIFICATIONS = True

# --------------------------------------------------------------------------------------------------#

# ROWS_PER_PAGE = 10

# --------------------------------------------------------------------------------------------------#

JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)

# --------------------------------------------------------------------------------------------------#
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# --------------------------------------------------------------------------------------------------#

API_VERSION = "1.0.0"
