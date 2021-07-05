from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired
import base64
import os
import datetime
import plaid
import json
import time
from flask import Flask
from flask import render_template
from flask import request
from flask import jsonify

class RoutineForm(FlaskForm):
    pass
    #email = StringField('email', validators=[DataRequired()])
    #phone = StringField('phone', validators=[DataRequired()])
    #password = PasswordField('Password', validators=[DataRequired()])
    #remember_me = BooleanField('Remember Me')
    #submit = SubmitField('Sign In')

class RoutineScreenField():
    def __init__(self, name):
        self.name = name
        self.label = 'label'
        self.Type = 'StringField'
        self.validators = 'DataRequired'

    def __repr__(self):
        return '<routine_screen_field {}>'.format(self.name)


