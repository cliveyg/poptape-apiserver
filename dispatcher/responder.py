# responder.py
# 
# builds a json response to the api request. sometimes we pass straight
# through to the microservice and simply relay the reply back to the client
# and sometimes we need to build a response from several microservices
from rest_framework import status
from rest_framework.response import Response
from reverse_proxy.microservice import fetch_data
from django.conf import settings
from celery import shared_task, group

import time
import json

from .tasks import get_microservice_data

# get an instance of a logger
import logging
logger = logging.getLogger('apiserver')

# -----------------------------------------------------------------------------

def BuildAPIResponse(**kwargs):

    request = kwargs['request']
    queryset = kwargs['qs']

    dicky = queryset.values('api_rules').get()

    if True == False: # dicky.get('login_api_url') == "MULTIPLE":
        logger.info("We are multi, man")
        pass
    else:
        logger.info("Pass thru like a hot curry: %s", dicky.get('api_rules'))
        #logger.info("Hot curry sauce")
        upstream_urls = dicky.get('api_rules')
        url_list = json.loads(upstream_urls)

        logger.info("Length of array is [%s]",url_list)


        #dict1 = queryset.values('login_api_url').get()
        #upstream_url = dict1.get('login_api_url')
        #upstream_server = settings.LOGIN_SERVER_URL
        #full_url = upstream_server + upstream_url
        full_url = "https://poptape.club/login/status"
        logger.info("FULL URL [%s]", full_url)
        #job = group([
        #    get_microservice_data
        #])
        #result = job.apply_async()
        result = get_microservice_data.apply_async()

        while not result.ready():
           pass 

        logger.info("Result id [%s]", result.id)

        logger.info("Actual result [%s]",result.result)
        result.forget()

        return fetch_data(request=request, upstream_url=full_url) 

    #return Response(queryset.values(), status=status.HTTP_200_OK)
    return Response({ 'foo': 'bar'}, status=417)

# -----------------------------------------------------------------------------

