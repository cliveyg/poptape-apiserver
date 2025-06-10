# reverse_proxy/microservice.py
# this module is basically a function based version of the ProxyView class

#TODO: move this and utils.py into a separate app in api server

from rest_framework import status
from rest_framework.response import Response
# from django.utils.six.moves.urllib.parse import urlparse, urlencode, quote_plus
from urllib.parse import urlparse, urlencode, quote_plus
from django.conf import settings
#from django.views.decorators.csrf import csrf_exempt

import requests 
from requests.auth import HTTPBasicAuth
import asyncio
import json

from .utils import normalize_request_headers, encode_items

# get an instance of a logger
import logging
logger = logging.getLogger('apiserver')

QUOTE_SAFE = r'<.;>\(}*+|~=-$/_:^@)[{]&\'!,"`'

# -----------------------------------------------------------------------------

def fetch_data(**kwargs):

    request = kwargs['request']
    upstream_urls = kwargs['upstream_urls']
    good_codes = kwargs['good_codes']
    # make good_codes an array
    good_codes = [int(i) for i in good_codes.split()]

    # make calls to microservices
    loop = asyncio.new_event_loop()

    tasks = []
    for url_dict in upstream_urls:
        tasks.append(_dispatch(request, url_dict))

    # get all the results from every http call
    async def main():
        results = await asyncio.gather(*tasks)
        return results

    # returns an array
    results = loop.run_until_complete(main())
    errors = []

    if len(results) > 0:
        ret_code = 200 # default ret code
        for result in results:
            if result['upresp'].status_code not in good_codes:
                # we overwrite codes here - so only the last 
                # bad code would be returned. revisit this
                if result['upresp'].status_code > ret_code:
                    ret_code = result['upresp'].status_code
                    try:
                        err_data = result['upresp'].json()
                    except Exception as e:
                        logger.error(e)
                        err_data = json.loads('{ "message": "No error data returned" }')

                    errors.append({ 'url': result['upresp'].url,
                                    'code': result['upresp'].status_code,
                                    'data': err_data })
                
        return ret_code, results, errors
    return 503, None

# -----------------------------------------------------------------------------

async def _dispatch(request, url_dict):

    #logger.debug("attempting to dispatch upstream...")

    upstream_url = url_dict['url']
    url_id = url_dict['track_id']

    #print("Up url is [%s]",upstream_url)

    #request_payload = request.body

    if request.GET:
        upstream_url += '?' + get_encoded_query_params(request)

    logger.debug("Upstream URL is [%s]", upstream_url)

    request_headers = get_request_headers(request)
    upstream_response = Response()

    try:
        if request.method == "GET":
            upstream_response = requests.get(upstream_url, headers=request_headers)
        elif request.method == "POST":
            upstream_response = requests.post(upstream_url, data=json.dumps(request.data), headers=request_headers)
        elif request.method == "PUT":
            upstream_response = requests.put(upstream_url, data=json.dumps(request.data), headers=request_headers)            
        elif request.method == "DELETE":
            upstream_response = requests.delete(upstream_url, headers=request_headers)         
    except requests.exceptions as error:
        #TODO: better error handling here
        logger.error(error)
        #upstream_response = 

    #return {'upresp': upstream_response, 'req': requests, 'track_id': url_id}
    return {'upresp': upstream_response, 'track_id': url_id}

# -----------------------------------------------------------------------------

def get_proxy_request_headers(request):
    # Get normalized headers for the upstream
    # Gets all headers from the original request and normalizes them.
    # Normalization occurs by removing the prefix ``HTTP_`` and
    # replacing and ``_`` by ``-``. Example: ``HTTP_ACCEPT_ENCODING``
    # becames ``Accept-Encoding``.
    # .. versionadded:: 0.9.1
    # :param request:  The original HTTPRequest instance
    # :returns:  Normalized headers for the upstream
    return normalize_request_headers(request)

# -----------------------------------------------------------------------------

def get_request_headers(request):
    # Return request headers that will be sent to upstream.
    # The header REMOTE_USER is set to the current user
    # if AuthenticationMiddleware is enabled and
    # the view's add_remote_user property is True.
    # .. versionadded:: 0.9.8
    request_headers = get_proxy_request_headers(request)

    return request_headers

# -----------------------------------------------------------------------------

def get_quoted_path(path):
    # Return quoted path to be used in proxied request"""
    return quote_plus(path.encode('utf8'), QUOTE_SAFE)

# -----------------------------------------------------------------------------

def get_encoded_query_params(request):
    # Return encoded query params to be used in proxied request"""
    get_data = encode_items(request.GET.lists())
    return urlencode(get_data)

# -----------------------------------------------------------------------------

