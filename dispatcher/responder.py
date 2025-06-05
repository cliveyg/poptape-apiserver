# dispatcher/responder.py
# 
# builds a json response to the api request. sometimes we pass straight
# through to the microservice and simply relay the reply back to the client
# and sometimes we need to build a response from several microservices
from rest_framework import status
from rest_framework.response import Response
from reverse_proxy.microservice import fetch_data
from django.conf import settings

import operator
import time
import json
import re
import os
import requests
from requests.auth import HTTPBasicAuth

# get an instance of a logger
import logging
logger = logging.getLogger('apiserver')

# -----------------------------------------------------------------------------

HOP_BY_HOP_HEADERS = ['Connection',
                      'Keep-Alive',
                      'Proxy-Authenticate',
                      'Proxy-Authorization',
                      'TE',
                      'Trailers',
                      'Transfer-Encoding',
                      'Content-Length',
                      'Upgrade']

# -----------------------------------------------------------------------------

def BuildAPIResponse(**kwargs):

    request = kwargs['request']
    queryset = kwargs['qs']
    url = kwargs['url']
    uuid1 = None
    if 'uuid1' in kwargs:
        uuid1 = kwargs['uuid1']

    logger.debug("BuildAPIResponse")

    dicky = queryset.values('api_rules').get()
    api_rules = dicky.get('api_rules')
    api_rules.replace('\\n', ' ').replace('\\t', ' ').replace('\\r', ' ')
    api_rules.replace('\n', ' ').replace('\t', ' ').replace('\r', ' ')
    logger.debug(api_rules)
    url_list = json.loads(api_rules)
    dick2 = queryset.values('expected_successful_responses').get()
    good_codes = dick2.get('expected_successful_responses')

    # we need to get the full url for each url. the reason we're doing
    # it this way is so we can get server names from the .env file
    full_urls = []
    fields =[]
    count = 1

    for destination in url_list:
        full_url = None
        fields_dict = None
        error = False

        if "/" in destination['url']:
            microservice_name, rest_of_url = destination['url'].split('/', 1)
        else:
            microservice_name = destination['url']
            rest_of_url = None
        
        #TODO: refactor this. don't like the hardcoded microservices here. 
        # maybe use an array that can be read from .env
        if microservice_name == 'authy':
            full_url = settings.LOGIN_SERVER_URL
        elif microservice_name == 'items':
            full_url = settings.ITEMS_SERVER_URL
        elif microservice_name == 'address':
            full_url = settings.ADDRESS_SERVER_URL
        elif microservice_name == 'aws':
            full_url = settings.AWS_SERVER_URL
        else:
            return Response({ 'message': 'Missing server URL' }, status=status.HTTP_501_NOT_IMPLEMENTED)

        #TODO: need to make this more general to accept more than one possible
        # variable

        if uuid1 is not None and destination['pass_data']:
            new_rest_of_url = re.sub('<uuid1>', str(uuid1), rest_of_url)
            full_url = full_url + microservice_name + "/" + new_rest_of_url
        elif rest_of_url != None:
            full_url = full_url + microservice_name + "/" + rest_of_url
        else:
            full_url = full_url + microservice_name

        
        # need some way of tracking which request/response is linked to which
        # api rule. a simple count can achieve this. we need to do this as we're 
        # sending async requests and can't guarantee return order
        dic_of_urls = {'track_id': count, 'url': full_url}
        dic_of_fields = {'track_id': count, 'fields': destination['fields']}

        if not error:
            full_urls.append(dic_of_urls)
            fields.append(dic_of_fields)
            count += 1

    logger.info("FULL OUTGOING URLS:")
    logger.info(full_urls)

    errors = []
    if len(full_urls) > 0: 
        status_code, data, errors = fetch_data(request=request, 
                                               good_codes=good_codes,
                                               upstream_urls=full_urls) 
        if status_code == 200:
            return _builder(data, fields, request.path, request.method, uuid1)
    
    if settings.ENVIRONMENT == "DEV":
        return Response({ 'errors': errors }, status=status_code)


    return Response({ 'message': 'unable to successfully build response' }, 
                    status=status_code)


# -----------------------------------------------------------------------------
# match returned results against the original api rules to know how to build
# the response with only desired fields. may also need to transform the names
# of the returned fields to something else

def _builder(results, fields, request_path, request_method, uuid):

    # the data should be in the form of an array of dicts. the dicts consists 
    # of a requests response and the original incoming request
    response_fields = []

    # we now create one big dictionary with all our returned data. that data
    # can be identified by the track_id and matched to what we want our 
    # output to be
    for result in results:
        requests_response = result['upresp']
        json_content = None
        try:
            json_content = requests_response.json()
        except ValueError as error:
            logger.error(str(error))
            pass

        json_content['track_id'] = result['track_id']
        response_fields.append(json_content)

    # this sorting/matching of data has only been tested on relatively
    # flat data structures. we may need some kind of recursion or something
    # else for more complicated bit's of data. refactor in the future

    # we are matching/sorting on our track_id 
    sorting_key = operator.itemgetter("track_id")
    response_fields = sorted(response_fields, key=sorting_key)
    fields = sorted(fields, key=sorting_key)
    out_dic = {}

    # we then use zip to join our dicts
    for big_dict, j in zip(response_fields, fields):
        big_dict.update(j)
        # we then match using sets / dicts
        for wanted_field in big_dict['fields']:
            for key in set(wanted_field) & set(big_dict):
                # and finally we want the value of the wanted field to be the
                # key of our new field and the value of that to be the returned 
                # value from the microservice(s). this effectively transforms
                # the name of the field to what we wanted from the api rules
                # database field
                out_dic[wanted_field.get(key)] = big_dict.get(key)

    if settings.ENVIRONMENT == "DEV":
        out_dic['request_url'] = request_path

    if uuid:
        out_dic['public_id'] = uuid

    stts = status.HTTP_200_OK
    if request_method == 'POST':
        stts = status.HTTP_201_CREATED
    return Response(out_dic, status=stts)

# -----------------------------------------------------------------------------
# need to remove any hop-by-hop headers and django says no to these and kicks
# up a fuss

def _build_headers(headers):

    new_headers = {}

    for (key, value) in headers.items():
        if key not in HOP_BY_HOP_HEADERS:
            new_headers[key] = value

    return new_headers

# -----------------------------------------------------------------------------

def _create_django_response_from_requests(response):

    headers = _build_headers(response.headers)

    return Response(response.json(), headers=headers, status=response.status_code)

