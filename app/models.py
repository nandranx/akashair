from datetime import datetime
from email.policy import default
from typing import Text
from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.dialects.postgresql import UUID
import uuid

@login_manager.user_loader
def load_user(id):
    try:
        return User.query.get(int(id))
    except:
        return None

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), index=True, unique=True) 
    email = db.Column(db.String(120), index=True, unique=True)
    first_name = db.Column(db.String(30))
    last_name = db.Column(db.String(30))
    password_hash = db.Column(db.String(128))
    user_groups = db.Column(db.String(128))
    admin = db.Column(db.Boolean)
    def __repr__(self):
        return '<user {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)    

class Metar(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    icao_code = db.Column(db.String(4))
    observation_time = db.Column(db.String(128))
    metar_raw_text = db.Column(db.String(128))
    def __repr__(self):
        return '<metar: {}>'.format(self.icao_code + '@' + self.observation_time) 

class MetarUpdates(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.String(128),default = datetime.utcnow())
    comments = db.Column(db.String(128))
    def __repr__(self):
        return '<metar: {}>'.format(self.icao_code + '@' + self.observation_time) 
