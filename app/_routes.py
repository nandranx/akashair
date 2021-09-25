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
            next_page = url_for('routine')
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

@app.route('/routine/<int:unique_id>', methods = ['GET','POST'])
@app.route('/routine/<int:unique_id>/', methods = ['GET','POST'])
@app.route('/routine', defaults={'unique_id': 0},    methods = ['GET','POST'])
@app.route('/routine/', defaults={'unique_id': 0}, methods = ['GET','POST'])
@login_required
def routine(unique_id):
    info = []
    form, info = my_view(info, unique_id)
    
    FieldEntries = []
    FieldEntry = {}

    if unique_id!=0:
        if form.validate_on_submit():
            #Add a new Routine to the database
            #for each_field in form:
            #    if each_field.type == "StringField" or each_field.type == "PasswordField":
            #        FieldEntry = {str(each_field.name) : str(each_field.data)}
            #        FieldEntries.append(FieldEntry)
            
            rs = RoutineScreen()
            rs.version_ = '1'
            rs.is_primary = True

            rs.reader = '1'
            rs.editor = '1'
            rs.entry_reader = '1'
            rs.entry_editor = '1'
            
            rs.name = form.name.data
            rs.label = form.label.data
            rs.description = form.description.data
            rs.fields = form.fields.data

            try:
                db.session.add(rs)
                db.session.commit()
            except Exception as error:
                info.append(error)

            return redirect(url_for('routine', unique_id=unique_id )), info

        return render_template('routine_entry_editor.html', title='Routine',form=form, unique_id=unique_id, info=info)
    else:
        routines = []
        rs_filtered = RoutineScreen.query.all() 
        for i in range(0,len(rs_filtered)):
            avbl_routine = ""
            avbl_routine = {"name" : str(rs_filtered[i].name),"id" : str(rs_filtered[i].id),"description" : str(rs_filtered[i].description) }
            routines.append(json.loads(json.dumps(avbl_routine)))

        return render_template('routine_index.html', title='Available Routines', routines=routines)
        


@app.errorhandler(404)
def not_found(e):
    """Page not found."""
    return make_response(render_template("404.html"),404)