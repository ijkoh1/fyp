from flask_wtf import Form
from wtforms import TextField, BooleanField, validators
from wtforms.validators import DataRequired

class DestinationForm(Form):
    start = TextField("StartPoint", [validators.Required("Please enter your location point.")])
    # dest = TextField("Destination", [validators.Required("Please enter your destination.")])
    remember_me = BooleanField('remember_me', default=False)
