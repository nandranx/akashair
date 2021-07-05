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

PLAID_CLIENT_ID = '5ec07fcefff2fe00139a2e2a'
PLAID_SECRET = '13153ba9e21edfad5264660d639254'
PLAID_REDIRECT_URI = 'http://localhost:8000/oauth-response.html'
# Use 'sandbox' to test with Plaid's Sandbox environment (username: user_good, password: pass_good)
PLAID_ENV = os.getenv('PLAID_ENV', 'sandbox')
PLAID_PRODUCTS = os.getenv('PLAID_PRODUCTS', 'transactions').split(',')
PLAID_COUNTRY_CODES = os.getenv('PLAID_COUNTRY_CODES', 'US').split(',')

def pretty_print_response(response):
  print(json.dumps(response, indent=2, sort_keys=True))

def empty_to_none(field):
  value = os.getenv(field)
  if value is None or len(value) == 0:
    return None
  return value

def create_link_token():
    client = plaid.Client(client_id=PLAID_CLIENT_ID,
                      secret=PLAID_SECRET,
                      environment=PLAID_ENV,
                      api_version='2019-05-29')

    try:
        link_token = client.LinkToken.create(
            {
            'user': {
                # This should correspond to a unique id for the current user.
                'client_user_id': 'user-id',
            },
            'client_name': "Plaid Quickstart",
            'products': PLAID_PRODUCTS,
            'country_codes': PLAID_COUNTRY_CODES,
            'language': "en",
            'redirect_uri': PLAID_REDIRECT_URI,
            }
        )
        return link_token

    except plaid.errors.PlaidError as e:
        return jsonify(format_error(e))

class ConnectForm(FlaskForm):
    connect = SubmitField('Connect')

    
