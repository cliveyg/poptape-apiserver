from django.core.exceptions import ValidationError
from jsonschema.exceptions import ValidationError as JsonValidatonError
#from django.utils.translation import gettext_lazy as _
from django.conf import settings
#from rest_framework import serializers
from jsonschema import validate
import json
from .assertions import assert_valid_schema
import os.path

# -----------------------------------------------------------------------------

def validate_apiserver_url(value):
    validate_url(value, settings.APISERVER_URL)

# -----------------------------------------------------------------------------
    
def validate_login_url(value):
    validate_url(value, settings.LOGIN_URL)

# -----------------------------------------------------------------------------

def validate_url(value, url):
    
    if isinstance(value, str) and (value.startswith(url) or value == "MULTIPLE"):
        pass
    else:
        raise ValidationError("URL doesn't start with the correct value")

# -----------------------------------------------------------------------------

def validate_api_rules(data):

    try:
        json_data = json.loads(data)
    except:
        raise ValidationError("Input is not valid json")

    # not fussed about being super quick here as validating urls when 
    # creating api paths is not an everyday occurence
    filepath = os.path.abspath(os.path.dirname(__file__))
    full_filename = filepath + '/schemas/api_rules.json'

    #assert_valid_schema(json_data, full_filename)
    pass
    try:
        assert_valid_schema(json_data, full_filename)
    except JsonValidatonError as error:
        raise ValidationError(error.message)

# -----------------------------------------------------------------------------
