from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from app.models import User

class appForm(FlaskForm):
    icao_codes = StringField('icao_codes', validators=[DataRequired()])
    submit = SubmitField('Get METARs')