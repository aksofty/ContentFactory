import os

from flask import Flask
from flask_appbuilder import AppBuilder
from flask_sqlalchemy import SQLAlchemy
from app.admin.utils import add_all_views, create_admin
from app import DB_PATH, BASE_DIR
from app.config import Config

template_folder = os.path.join(BASE_DIR, 'admin', 'templates')

app = Flask(__name__, template_folder=template_folder)

app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{DB_PATH}"
app.config['SECRET_KEY'] = Config.ADMIN_SECRET
app.config['CSRF_ENABLED'] = True
app.config['APP_NAME'] = "ContentFactory"

db = SQLAlchemy(app)

with app.app_context():
    appbuilder = AppBuilder(app, db.session) # type: ignore
    add_all_views(appbuilder)
    create_admin(appbuilder, Config.ADMIN_NAME, Config.ADMIN_PASS)

if __name__ == "__main__":
    app.run("0.0.0.0", 8080, debug=False)