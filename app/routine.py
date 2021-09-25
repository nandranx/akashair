from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Optional
import base64
import os
import datetime
import plaid
import json
import time
from app import app
from app import db
from app.models import User, RoutineScreen, RoutineEntry
from flask import Flask, make_response, render_template, request, jsonify

class RoutineForm(FlaskForm):

    def __repr__(self):
        return '<RoutineForm Object>'

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
        return '<RoutineScreenField {}>'.format(self.name)


def my_view(info, unique_id):
    class F(RoutineForm):
        pass

    # F.username = StringField('username')
    # setattr(F, 'name_mv2', StringField('title_mv2'))
    
    try:
        rs = RoutineScreen.query.filter_by(id=unique_id).first()
        fields=[]
        fields = json.loads(rs.fields)
        # flash (len(fields))
        # info.append('**********')
        for j in range(0, len(fields)):
            if fields[j]['validators'] == 'DataRequired':
                field_validators = DataRequired()

            if fields[j]['validators'] == '':
                field_validators = Optional()

            if fields[j]['type']:
                setattr(F, fields[j]['name'],StringField(fields[j]['label'], validators=[field_validators]))
                    
        setattr(F, 'create_request', SubmitField('Create Request'))

        return F(), info

    except Exception as error:
        info.append("error : " + "No such form exists. Please select the right form from url")
        return F(), info

def add_routine_screen(unique_id, info):
    array = [
        { 
        "name" : "version",
        "label" : "version",
        "type" : "Integer",
        "validators" : ""
        },
        { 
        "name" : "is_primary",
        "label" : "is_primary",
        "type" : "Boolean",
        "validators" : ""
        },
        { 
        "name" : "name",
        "label" : "name",
        "type" : "String",
        "validators" : ""
        },
        { 
        "name" : "label",
        "label" : "label",
        "type" : "String",
        "validators" : ""
        },
        { 
        "name" : "description",
        "label" : "description",
        "type" : "String",
        "validators" : ""
        },
        { 
        "name" : "fields",
        "label" : "fields",
        "type" : "String",
        "validators" : ""
        },
        { 
        "name" : "reader",
        "label" : "reader",
        "type" : "Integer",
        "validators" : ""
        },
        { 
        "name" : "editor",
        "label" : "editor",
        "type" : "Integer",
        "validators" : ""
        },
        { 
        "name" : "entry_reader",
        "label" : "entry_reader",
        "type" : "Integer",
        "validators" : ""
        },
        { 
        "name" : "entry_editor",
        "label" : "entry_editor",
        "type" : "Integer",
        "validators" : ""
        }]

    rs = RoutineScreen()
    rs.version_ = '1'
    rs.is_primary = True

    rs.reader = '1'
    rs.editor = '1'
    rs.entry_reader = '1'
    rs.entry_editor = '1'
    
    rs.name = 'RoutineScreen_form_name_{}'.format(unique_id)
    rs.label = 'label_{}'.format(unique_id)
    rs.description = 'description_{}'.format(unique_id)
    rs.fields = json.dumps(array,indent=4)

    try:
        db.session.add(rs)
        db.session.commit()
    except Exception as error:
        info.append(error)
    return info


