from django.core.exceptions import ValidationError
from jsonschema.exceptions import ValidationError as JsonValidatonError
#from django.utils.translation import gettext_lazy as _
from django.conf import settings
#from rest_framework import serializers
from jsonschema import validate
import json
from apiserver.assertions import assert_valid_schema
import os.path

# get an instance of a logger
import logging
logger = logging.getLogger('apiserver')

# define what we consider to be good http status codes - generally anything 
# 2xx upto 4xx. i'm considering return codes such as 404 to be valid for our
# purposes. might need to revisit this.
GOOD_HTTP_CODES = {200, 201, 202, 204, 301, 302, 303, 307, 308, 400,
                   401, 402, 403, 404, 405, 406, 407, 408, 409, 410, 
                   411, 412, 413, 414, 415, 416, 417, 418, 429}

# -----------------------------------------------------------------------------

def validate_apiserver_url(value):
    validate_url(value, settings.APISERVER_URL)

# -----------------------------------------------------------------------------
    
def validate_login_url(value):
    validate_url(value, settings.LOGIN_URL)

# -----------------------------------------------------------------------------

def validate_url(value, url):
    
    if isinstance(value, str) and value.startswith(url):
        pass
    else:
        raise ValidationError("URL doesn't start with the correct value")

# -----------------------------------------------------------------------------

def validate_http_codes(data):

    logger.info(type(data))
    logger.info("Data is [%s]", data)
    # this will error if the supplied data is not a list of integers
    # separated by a space
    try:
        data = [int(i) for i in data.split()]
    except:
        raise ValidationError("Must be a list of integers separated by spaces")

    # convert array to a set for comparison to our accepted http codes
    test_set = set(data)
    bad_juju = test_set.difference(GOOD_HTTP_CODES)

    if len(bad_juju) > 0:
        raise ValidationError("Unacceptable status code values")

    #json_schema_validation(data, '/schemas/http_codes.json')

# -----------------------------------------------------------------------------

def validate_api_rules(data):

    json_schema_validation(data, '/schemas/api_rules.json')

# -----------------------------------------------------------------------------

def json_schema_validation(data, schema_uri):

    try:
        json_data = json.loads(data)
    except:
        raise ValidationError("Input is not valid json")

    # not fussed about being super quick here as validating urls when 
    # creating api paths is not an everyminute occurence only when 
    # creating a record
    filepath = os.path.abspath(os.path.dirname(__file__))
    full_filename = filepath + schema_uri

    try:
        assert_valid_schema(json_data, full_filename)
    except JsonValidatonError as error:
        raise ValidationError(error.message)

