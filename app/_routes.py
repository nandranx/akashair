import os
from os import error

from app import app
from app import db

import json
import random
import uuid

from app.apppy import appForm
from app.login import LoginForm
from app.models import User
from app.register import RegistrationForm

from flask import render_template, flash, redirect, url_for, send_from_directory
from flask_login import current_user, login_user, login_required, logout_user

from flask_wtf import FlaskForm

from flask import request,  make_response
from werkzeug.urls import url_parse

from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Optional, InputRequired
from sqlalchemy.exc import IntegrityError

import requests
from bs4 import BeautifulSoup
import time
import atexit
from flask_apscheduler import APScheduler
from apscheduler.schedulers.background import BackgroundScheduler
import re

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
            next_page = url_for('app_home',icao_code='KSFO')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

x = "." 

def get_metars():
    metars = requests.get("https://aviationweather-cprk.ncep.noaa.gov/adds/dataserver_current/current/metars.cache.xml")
    open('now.xml', 'wb').write(metars.content)
    x = metars.content
    
scheduler = BackgroundScheduler()
scheduler.add_job(func=get_metars, trigger="interval", seconds=300)
scheduler.start()

# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('app_home',icao_codes='KSFO'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/akashair/<string:icao_code>', methods = ['GET','POST'])
@login_required
def app_home(icao_code='KSFO'):
    form = appForm()
    if form.validate_on_submit():
        return redirect(url_for('app_home', icao_code=request.form.get("icao_codes") ))

    icao_codes = re.split(' |,|\*|\n|  ',icao_code)
    metar = []

    soup = BeautifulSoup(open('now.xml', 'r').read(), 'lxml')

    for i in range(0,len(icao_codes)):
        try:
            metar_entry = { "icao_code" : icao_codes[i], "metar_raw_text" : soup.find("station_id",text=icao_codes[i]).find_parent().raw_text.text,"observation_time" : soup.find("station_id",text=icao_codes[i]).find_parent().observation_time.text }
            metar.append(json.loads(json.dumps(metar_entry)))
        except:
            metar_entry = { "icao_code" : icao_codes[i], "metar_raw_text" : "No such airport found" }
            metar.append(json.loads(json.dumps(metar_entry)))
    
    return render_template('app_templates/index.html', title='Available Routines', metar = metar, form = form)



@app.errorhandler(404)
def not_found(e):
    """Page not found."""
    return make_response(render_template("404.html"),404)