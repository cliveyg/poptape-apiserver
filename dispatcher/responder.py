# dispatcher/responder.py
# 
# builds a json response to the api request. sometimes we pass straight
# through to the microservice and simply relay the reply back to the client
# and sometimes we need to build a response from several microservices
from rest_framework import status
from rest_framework.response import Response
from reverse_proxy.microservice import fetch_data
from django.conf import settings

import time
import json
import re
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
    uuid = None
    if 'uuid' in kwargs:
        uuid = kwargs['uuid']

    dicky = queryset.values('api_rules').get()
    url_list = json.loads(dicky.get('api_rules'))    
    logger.info("No of tings returned from qs is [%]", len(url_list))

    # we need to get the full url for each url. the reason we're doing
    # it this way is so we can get server names from the .env file
    full_urls = []
    error = False
    fields =[]
    count = 1

    for destination in url_list:
        full_url = None
        fields_dict = None

        if "/" in destination['url']:
            microservice_name, rest_of_url = destination['url'].split('/', 1)
        else:
            microservice_name = destination['url']
            rest_of_url = None
        
        if microservice_name == 'login':
            full_url = settings.LOGIN_SERVER_URL
        elif microservice_name == 'items':
            full_url = settings.ITEMS_SERVER_URL
        else:
            error = True

        #TODO: need to make this more general to accept more than one possible
        # variable
        if uuid:
            new_rest_of_url = re.sub('<public_id>', uuid, rest_of_url)
            full_url = full_url + microservice_name + "/" + new_rest_of_url
        elif rest_of_url != None:
            full_url = full_url + microservice_name + "/" + rest_of_url
        else:
            full_url = full_url + microservice_name

        
        # need some way of tracking which request/response is linked to which
        # api rule. a simple count can achieve this
        dic_of_urls = {'id': count, 'url': full_url}
        dic_of_fields = {'id': count, 'fields': destination['fields']}

        if not error:
            full_urls.append(dic_of_urls)
            fields.append(dic_of_fields)
            count += 1

    if len(full_urls) > 0: 
        status_code, data = fetch_data(request=request, upstream_urls=full_urls) 
        if status_code == 200:
            return _builder(data, fields, request.path, uuid)
        
    return Response({ 'message': 'unable to succesfully construct response' }, status=status.HTTP_417_EXPECTATION_FAILED)

# -----------------------------------------------------------------------------
# match returned results against the original api rules to know how to build
# the response with only selected fields

def _builder(results, fields, request_path, uuid):

    # the data should be in the form of an array of dicts. the dicts consists 
    # of a requests response and the original incoming request
    response_fields = []

    for result in results:
        logger.debug(result)
        requests_response = result['upresp']
        try:
            json_content = requests_response.json()
        except ValueError as error:
            logger.error(str(error))
            pass

        response_fields.append(json_content)

    #TODO: need to delete unwanted fields 

    
    if uuid:
        return Response({ 'public_id': uuid,
                          'request_url': request_path, 
                          'fields': response_fields }, 
                          status=status.HTTP_200_OK) 

    return Response({ 'request_url': request_path,
                      'fields': response_fields },
                      status=status.HTTP_200_OK)

# -----------------------------------------------------------------------------
# need to remove any hop-by-hop headers and django says no to these and kicks
# up a fuss

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

