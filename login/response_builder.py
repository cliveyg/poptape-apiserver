# response_builder.py
# 
# builds a json response to the api request. sometimes we pass straight
# through to the microservice and simply relay the reply back to the client
# and sometimes we need to build a response from several micorservices
from rest_framework import status
from rest_framework.response import Response
from reverse_proxy.views import ProxyView
from reverse_proxy.microservice import fetch_data

# get an instance of a logger
import logging
logger = logging.getLogger('apiserver')

# -----------------------------------------------------------------------------

def BuildAPIResponse(**kwargs):

    request = kwargs['request']
    queryset = kwargs['qs']

    dicky = queryset.values('login_api_url').get()

    if dicky.get('login_api_url') == "MULTIPLE":
        logger.info("We are multi, man")
        pass
    else:
        logger.info("Pass thru like a hot curry [%s]", dicky.get('login_api_url'))
        upstream_url = dicky.get('login_api_url')
        return fetch_data(request=request, qs=queryset) 
        #return GetMyStuff.as_view(upstream='https://poptape.club/login/status')
        #logger.info("Proxy View Response [%s]", proxy_response)
        #return proxy_response
        #return proxy_view.upstream(dicky.get('login_api_url'))
        #logger.info("Pass thru like a hot curry [%s]", dicky.get('login_api_url'))
        #pass

    return Response(queryset.values(), status=status.HTTP_200_OK)

    # return a reduced set of the data for non-authenticated requests
    #if request.user.is_authenticated:
    #    proxy_view = ProxyView.as_view() 
    #    logger.info("you're alright")
    #    return Response(queryset.values(), status=status.HTTP_200_OK)    
    #else:
    #    logger.info("only so far")
    #    return Response(queryset.values('apiserver_url', 'methods'), status=status.HTTP_200_OK)

# -----------------------------------------------------------------------------

