import os
from os import error

from app import app
from app import db

import json
import random
import uuid

from app.login import LoginForm
from app.routine import RoutineForm, RoutineScreenField, my_view, add_routine_screen
from app.connect import ConnectForm, create_link_token
from app.models import User, RoutineScreen, RoutineEntry
from app.register import RegistrationForm

from flask import render_template, flash, redirect, url_for, send_from_directory
from flask_login import current_user, login_user, login_required, logout_user

from flask_wtf import FlaskForm

from flask import request,  make_response
from werkzeug.urls import url_parse

from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Optional, InputRequired
from sqlalchemy.exc import IntegrityError

@app.route('/')
@app.route('/index', methods = ['GET','POST'])
def index():
    return render_template('index.html', title='Home')
    
@app.route('/login', methods = ['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('routine_home')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('routine'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/connect', methods = ['GET','POST'])
def connect() :
    form = ConnectForm()
    if form.validate_on_submit():
        return redirect(url_for('connect'))
    return render_template('connect.html', title='Home',form=form, link_token=create_link_token())

@app.route('/routine/<int:unique_id>/', methods = ['GET','POST'])
@login_required
def routine(unique_id):
    info = []

    form, info = my_view(info, unique_id)
    FieldEntries = []
    FieldEntry = {}
        
    if form.validate_on_submit():
        re = RoutineEntry()
        re.version_ = '1'
        re.routine_form_id = unique_id
        re.routine_form_verion = '1'
        re.field_values = form.fields.data

        try:
            db.session.add(re)
            db.session.commit()
        except Exception as error:
            info.append(error)

        return redirect(url_for('routine', unique_id=unique_id )), info

    return render_template('routine_entry/creator.html', title='Routine',form=form, unique_id=unique_id, info=info)        

@app.route('/routine/', methods = ['GET','POST'])
@login_required
def routine_redirect():
    return redirect(url_for('routine_home'))

@app.route('/routine/home/', methods = ['GET','POST'])
@login_required
def routine_home():
    routines = []
    rs_filtered = RoutineScreen.query.all() 
    for i in range(0,len(rs_filtered)):
        avbl_routine = ""
        avbl_routine = {"name" : str(rs_filtered[i].name),"id" : str(rs_filtered[i].id),"description" : str(rs_filtered[i].description) }
        routines.append(json.loads(json.dumps(avbl_routine)))

    return render_template('routine/index.html', title='Available Routines', routines=routines)
        
@app.route('/routine/<int:unique_id>/view', methods = ['GET','POST'])
@login_required
def routine_entry():
    routines = []
    rs_filtered = RoutineScreen.query.all() 
    for i in range(0,len(rs_filtered)):
        avbl_routine = ""
        avbl_routine = {"name" : str(rs_filtered[i].name),"id" : str(rs_filtered[i].id),"description" : str(rs_filtered[i].description) }
        routines.append(json.loads(json.dumps(avbl_routine)))

    return render_template('routine_entry/index.html', title='Available Routines', routines=routines)
        

@app.errorhandler(404)
def not_found(e):
    """Page not found."""
    return make_response(render_template("404.html"),404)