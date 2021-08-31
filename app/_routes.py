import os
from os import error
from flask import render_template, flash, redirect, url_for, send_from_directory
from app import app
from app import db
import json
from app.login import LoginForm
from app.routine import RoutineForm, RoutineScreenField
from app.connect import ConnectForm, create_link_token
from app.models import user, RoutineScreen, RoutineEntry
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Optional, InputRequired
from sqlalchemy.exc import IntegrityError
import random

@app.route('/')
@app.route('/index', methods = ['GET','POST'])
def index():
    return render_template('index.html', title='Home')
    
@app.route('/login', methods = ['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for user {}, remember_me={}'.format(
            form.email.data, form.remember_me.data))
        return redirect('/connect')
        return redirect(url_for('index'))
    return render_template('login.html',title='Log in', form=LoginForm())

@app.route('/connect', methods = ['GET','POST'])
def connect() :
    form = ConnectForm()
    if form.validate_on_submit():
        return redirect(url_for('connect'))
    return render_template('connect.html', title='Home',form=form, link_token=create_link_token())

@app.route('/routine', defaults={'unique_id': 0},    methods = ['GET','POST'])
@app.route('/routine/', defaults={'unique_id': 0}, methods = ['GET','POST'])
@app.route('/routine/<unique_id>', methods = ['GET','POST'])
@app.route('/routine/<unique_id>/', methods = ['GET','POST'])
def routine(unique_id):
    info = []
    form, info = my_view(info, unique_id)
    
    FieldEntries = []
    FieldEntry = {}

    if unique_id!=0:
        if form.validate_on_submit():
            for each_field in form:
                if each_field.type == "StringField" or each_field.type == "PasswordField":
                    FieldEntry = {str(each_field.name) : str(each_field.data)}
                    FieldEntries.append(FieldEntry)
            flash(json.dumps(FieldEntries))

            return redirect(url_for('routine', unique_id ))
        return render_template('routine.html', title='Routine',form=form, unique_id=unique_id, info=info)
    else:
        routines = []
        rs_filtered = RoutineScreen.query.all() 
        for i in range(0,len(rs_filtered)):
            avbl_routine = ""
            avbl_routine = {"name" : str(rs_filtered[i].name),"id" : str(rs_filtered[i].id),"description" : str(rs_filtered[i].description) }
            routines.append(json.loads(json.dumps(avbl_routine)))

        return render_template('routine_index.html', title='Available Routines', routines=routines)
        
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
        "name" : 'id',
        "label" : 'id',
        "type" : 'Integer',
        "validators" : ''
        },
        { 
        "name" : 'version',
        "label" : 'version',
        "type" : 'Integer',
        "validators" : ''
        },
        { 
        "name" : 'is_primary',
        "label" : 'is_primary',
        "type" : 'Boolean',
        "validators" : ''
        },
        { 
        "name" : 'name',
        "label" : 'name',
        "type" : 'String',
        "validators" : ''
        },
        { 
        "name" : 'label',
        "label" : 'label',
        "type" : 'String',
        "validators" : ''
        },
        { 
        "name" : 'description',
        "label" : 'description',
        "type" : 'String',
        "validators" : ''
        },
        { 
        "name" : 'fields',
        "label" : 'fields',
        "type" : 'String',
        "validators" : ''
        },
        { 
        "name" : 'reader',
        "label" : 'reader',
        "type" : 'Integer',
        "validators" : ''
        },
        { 
        "name" : 'editor',
        "label" : 'editor',
        "type" : 'Integer',
        "validators" : ''
        },
        { 
        "name" : 'entry_reader',
        "label" : 'entry_reader',
        "type" : 'Integer',
        "validators" : ''
        },
        { 
        "name" : 'entry_editor',
        "label" : 'entry_editor',
        "type" : 'Integer',
        "validators" : ''
        }]

    rs = RoutineScreen()
    rs.id_num = unique_id
    rs.version_ = '1'
    rs.is_primary = True
    rs.reader = '1'
    rs.editor = '1'
    rs.entry_reader = '1'
    rs.entry_editor = '1'
    rs.name = 'RoutineScreen_form_name_{}'.format(unique_id)
    rs.label = 'label_{}'.format(unique_id)
    rs.description = 'description{}'.format(unique_id)
    rs.fields = json.dumps(array,indent=4)

    try:
        db.session.add(rs)
        db.session.commit()
    except Exception as error:
        info.append(error)
    return info

