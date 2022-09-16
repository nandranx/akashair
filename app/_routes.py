from datetime import datetime
import os
from os import error

from app import app
from app import db

import json
import random
import uuid

from app.apppy import akashairForm
from app.login import LoginForm
from app.models import User, Metar
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
    # if the user is logged in, redirect to index
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()

    #log the user in
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

#variable to store the metars xml downoaded from noaa.gov
metars_xml = "." 

def get_metars():
    metars = requests.get("https://aviationweather-cprk.ncep.noaa.gov/adds/dataserver_current/current/metars.cache.xml")
    #open('now.xml','wb').write(metars.content)
    #x = BeautifulSoup(open('now.xml', 'r').read(), features='xml')
    metars_xml = BeautifulSoup(metars.text,'lxml')
    
    # find all instances of a metar from the xml
    metars_array = metars_xml.find_all('metar')
    if (len(metars_array)==0):
        metars_array = metars_xml.find_all('METAR')
    
    #For each metar entry, add it to the databse
    for i in range(0,len(metars_array)):
        metar = Metar(icao_code=metars_array[i].station_id.text, observation_time=metars_array[i].observation_time.text, metar_raw_text=metars_array[i].raw_text.text )
        db.session.add(metar)
    db.session.commit()

#Scheduler to get fresh metars every 5 mins
scheduler = BackgroundScheduler()
scheduler.add_job(func=get_metars, trigger="interval", seconds=300)
scheduler.start()
# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())

#Create account flow
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('app_home',icao_code='KSFO'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

#Get metars by providing an icao airport code
@app.route('/akashair/<string:icao_code>', methods = ['GET','POST'])
def app_home(icao_code='KSFO'):
    ### times.append("START: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3])

    form = akashairForm()
    if form.validate_on_submit():
        return redirect(url_for('app_home', icao_code=request.form.get("icao_codes") ))

    icao_codes = re.split(' |,|\*|\n|  ',icao_code)
    ### soup = BeautifulSoup(open('now.xml', 'r').read(), 'lxml')
    ### soup = BeautifulSoup(open('now.xml', 'r').read(), 'lxml')

    # Read metars for the requested airport from the database
    metar_data = []
    for i in range(0,len(icao_codes)):
        try:
            #metar_entry = { "icao_code" : icao_codes[i], "metar_raw_text" : soup.find("station_id",text=icao_codes[i]).find_parent().raw_text.text,"observation_time" : soup.find("station_id",text=icao_codes[i]).find_parent().observation_time.text }
            metar = Metar.query.filter_by(icao_code=icao_codes[i]).order_by(Metar.observation_time.desc()).first()
            metar_entry = { "icao_code" : metar.icao_code, "metar_raw_text" : metar.metar_raw_text,"observation_time" : metar.observation_time }
            metar_data.append(json.loads(json.dumps(metar_entry)))
        except:
            print("except")
            metar_entry = { "icao_code" : icao_codes[i], "metar_raw_text" : "No such airport found" }
            metar_data.append(json.loads(json.dumps(metar_entry)))
    
    #render the metars according to the template
    return render_template('app_templates/index.html', title='Available Routines', metar_data = metar_data, form = form)

@app.route('/admin', methods = ['GET','POST'])
@login_required
def admin():
    #get_metars()
    if current_user.admin == True :
        return render_template('app_templates/admin.html', title='ADMIN')


@app.errorhandler(404)
def not_found(e):
    """Page not found."""
    return make_response(render_template("404.html"),404)