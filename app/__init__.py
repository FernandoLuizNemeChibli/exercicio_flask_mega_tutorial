from config import base_dir
from flask import Flask
from flask_login import LoginManager
from flask_openid import OpenID
from flask_sqlalchemy import SQLAlchemy
from os import path

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)
lm = LoginManager()
lm.init_app(app)
lm.login_view='login'
oid = OpenID(app,path.join(base_dir,'tmp'))

from app import views
from app import models
