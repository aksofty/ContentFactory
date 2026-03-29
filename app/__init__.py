import os
from app.config import Config

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, 'data', Config.DB_NAME)
LOG_PATH = os.path.join(BASE_DIR, 'logs', Config.LOG_FILE)