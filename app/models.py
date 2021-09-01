from datetime import datetime
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
    def __repr__(self):
        return '<user {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)    

class RoutineScreen(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    version = db.Column(db.Integer)
    is_primary = db.Column(db.Boolean)

    reader = db.Column(db.Integer, db.ForeignKey('user.id'))
    editor = db.Column(db.Integer, db.ForeignKey('user.id'))
    entry_reader = db.Column(db.Integer, db.ForeignKey('user.id'))
    entry_editor = db.Column(db.Integer, db.ForeignKey('user.id'))

    name = db.Column(db.String(30))
    description = db.Column(db.String(150))
    fields =  db.Column(db.Text)

    created_at = db.Column(db.DateTime,default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'),default=1)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    last_updated_by = db.Column(db.Integer, db.ForeignKey('user.id'),default=1)
    deleted_at = db.Column(db.DateTime)

    def __repr__(self):
        return '<RoutineScreen {}>'.format(self.name)

class RoutineEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    version = db.Column(db.Integer)
    is_primary = db.Column(db.Boolean)
    
    routine_form_id = db.Column(db.Integer)
    routine_form_verion = db.Column(db.Integer)

    reader = db.Column(db.Integer, db.ForeignKey('user.id'))
    editor = db.Column(db.Integer, db.ForeignKey('user.id'))

    field_values = db.Column(db.Text)

    created_at = db.Column(db.DateTime,default=datetime.utcnow)
    created_by = db.Column(db.Integer,db.ForeignKey('user.id'),default=1)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    last_updated_by = db.Column(db.Integer,db.ForeignKey('user.id'),default=1)
    deleted_at = db.Column(db.DateTime)

    def __repr__(self):
        return '<RoutineEntry {}>'.format(self.id)