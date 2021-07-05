from os import error
from flask import render_template, flash, redirect, url_for
from app import app
from app import db
import json
from app.login import LoginForm
from app.routine import RoutineForm, RoutineScreenField
from app.connect import ConnectForm, create_link_token
from app.models import user, RoutineScreen, RoutineEntry
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Optional
from sqlalchemy.exc import IntegrityError

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

@app.route('/routine', defaults={'input': 1})
@app.route('/routine/', defaults={'input': 1})
@app.route('/routine/<input>', methods = ['GET','POST'])
@app.route('/routine/<input>/', methods = ['GET','POST'])
def routine(input):
    form, info = my_view(input)

    if form.validate_on_submit():
        return redirect(url_for('routine', input = input))

    return render_template('routine.html', title='Routine',form=form, input=input, info=info)

def my_view(unique_id=1):

    info = []
    fields = ''

    try:
        rs = RoutineScreen.query.all()
        for i in range(0,1):
            fields = json.loads(rs[i].fields)
            for j in range(0,len(fields)):
                if fields[j]['validators'] == 'DataRequired' :
                    field_validators = DataRequired()
            
                if fields[j]['validators'] == '' :
                    field_validators = Optional()

                if fields[j]['type']:
                    setattr(RoutineForm, fields[j]['name'], StringField(fields[j]['label'],validators=[field_validators]))
            setattr(RoutineForm, rs[i].name, SubmitField('Submit'))

    except Exception as error:
        info.append("error=" + str(error))

    #info = add_routine_screen(unique_id, info)
    
    return RoutineForm(), info

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
    rs.id = unique_id
    rs.version = '1'
    rs.is_primary = True
    rs.reader = '1'
    rs.editor = '1'
    rs.entry_reader = '1'
    rs.entry_editor = '1'
    rs.name = 'trial_name_{}'.format(unique_id)
    rs.label = 'label_{}'.format(unique_id)
    rs.description = 'description{}'.format(unique_id)
    rs.fields = json.dumps(array,indent=4)

    try:
        db.session.add(rs)
        db.session.commit()
    except Exception as error:
        info.append(error)
    return info
