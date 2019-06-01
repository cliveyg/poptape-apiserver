# apiserver/views.py
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import RetrieveAPIView
from django.http import JsonResponse
from rest_framework.views import APIView
from django.conf import settings

from reverse_proxy.microservice import fetch_data

# get an instance of a logger
import logging
logger = logging.getLogger('apiserver')

# -----------------------------------------------------------------------------
# view to show status of api server - doesn't require authentication

class StatusView(RetrieveAPIView):

    def get(self, request, *args, **kwargs):
        # simply returns a 200 ok with a message 
        logger.info("apiserver/views/StatusView.get")

        message = { 'message': 'System running...' }

        return Response(message, status=status.HTTP_200_OK)

# -----------------------------------------------------------------------------
# view to show status of all microservices - requires authentication

class AllStatusView(RetrieveAPIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        # simply returns a 200 ok with a message
        logger.info("apiserver/views/AllStatusView.get")

        url_list = []
        
        login_status_url = settings.LOGIN_SERVER_URL+ "login/status"
        url_list.append({'track_id': 1, 'url': login_status_url})

        items_status_url = settings.ITEMS_SERVER_URL+ "items/status"
        url_list.append({'track_id': 2, 'url': items_status_url})

        address_status_url = settings.ADDRESS_SERVER_URL+ "address/status"
        url_list.append({'track_id': 3, 'url': address_status_url})        

        # call all microservices
        status_code, results, errors = fetch_data(request=request,
                                                  good_codes="200",
                                                  upstream_urls=url_list)        

        # build our response
        constructed_results = []
        for result in results:
                message = result['upresp'].json()
                constructed_results.append({ 'url': result['upresp'].url,
                                             'code': result['upresp'].status_code,
                                             'message': message.get('message') })            


        data = { 'request_url': request.path, 
                 'results': constructed_results }

        return Response(data, status=status.HTTP_200_OK)

# -----------------------------------------------------------------------------
