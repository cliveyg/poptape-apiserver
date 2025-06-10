from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated, AllowAny

import apiserver.settings
#from apiserver.csrfexemption import CsrfExemptSessionAuthentication
from apiserver.authentication import CsrfExemptSessionAuthentication
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework.generics import ListCreateAPIView, ListAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.views import APIView

from dispatcher.models import URL
from dispatcher.serializers import URLSerializer
from dispatcher.responder import build_api_response

#from django.conf import settings
import json

# get an instance of a logger
import logging
logger = logging.getLogger('apiserver')

# -----------------------------------------------------------------------------

class CreateView(ListCreateAPIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)

    # this class defines the create behavior of our rest api
    queryset = URL.objects.all()
    serializer_class = URLSerializer

    def perform_create(self, serializer):
        # save the post data when creating a new url
        serializer.save()


    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        only_active_urls = queryset.filter(active=True)

        return Response(only_active_urls.values('apiserver_url', 'methods'), status=status.HTTP_200_OK)

# -----------------------------------------------------------------------------

class DetailsView(RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)

    # This class handles the http GET, PUT and DELETE requests.
    queryset = URL.objects.all()
    serializer_class = URLSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        return Response(queryset.values(), status=status.HTTP_200_OK)

# -----------------------------------------------------------------------------

#@csrf_exempt
class GetMicroserviceData(APIView):
    #permission_classes = (IsAuthenticatedOrReadOnly,)
    #authentication_classes = (CsrfExemptSessionAuthentication, )
    permission_classes = (AllowAny, )
    #authentication_classes = (CsrfExemptSessionAuthentication,)
    authentication_classes = ()

    # retrieves a model based on the inbound url
    #def initial(self, request, *args, **kwargs):
    #    #logger.info("In GetMicroserviceData.initial")


    def get(self, request, **kwargs):
        logger.info("In GetMicroserviceData.get")
        return _call_response_builder(request, **kwargs)

    def post(self, request, *args, **kwargs):
        logger.info("In GetMicroserviceData.post")
        return _call_response_builder(request, **kwargs)

    def put(self, request, *args, **kwargs):
        return JsonResponse({ 'message': 'put: nowt ere yet mate' }, status=418)

    def delete(self, request, *args, **kwargs):
        return JsonResponse({ 'message': 'delete: nowt ere yet mate' }, status=418)

# -----------------------------------------------------------------------------

class GetMicroURL(ListAPIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    authentication_classes = (CsrfExemptSessionAuthentication, )

    # retrieves a model based on the inbound url

    serializer_class = URLSerializer

    def dispatch(self, request, *args, **kwargs):
        return super(GetMicroURL, self).dispatch(request, *args, **kwargs)


    def get_queryset(self):
        # 
        self.micro_url = self.kwargs['micro_url']

        if 'uuid' in self.kwargs:
            self.uuid = self.kwargs['uuid']
        else:
            self.uuid = None

        # only return the object if it's active and should only return exact match if there is not a uuid
        # in url
        if self.uuid:
            url_model = URL.objects.filter(apiserver_url__icontains=self.micro_url).filter(active=True)
        else:
            url_model = URL.objects.filter(apiserver_url=self.micro_url).filter(active=True)

        return url_model


    # override the list method so we can return whatever status codes we need

    def list(self, request, *args, **kwargs):

        queryset = self.filter_queryset(self.get_queryset())
        passes, response = _passes_basic_checks(request, queryset, self.micro_url)

        if not passes:
            return response

        # we passed the basic checks so continue
        if self.uuid:
            return build_api_response(request=request, qs=queryset, url=self.micro_url, uuid=self.uuid)
        else:
            return build_api_response(request=request, qs=queryset, url=self.micro_url)

# -----------------------------------------------------------------------------

class GetItemURL(ListAPIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    #authentication_classes = (CsrfExemptSessionAuthentication,)

    # retrieves a model based on the inbound url

    serializer_class = URLSerializer

# -----------------------------------------------------------------------------

def _call_response_builder(request, **kwargs):

        micro_url = apiserver.settings.APISERVER_URL + kwargs.get('micro_url')
        uuid1 = kwargs.get('uuid1')

        logger.debug("MicroURL is [%s]", micro_url)
        logger.debug("UUID1 is [%s]", uuid1)
        logger.debug("req.GET.dict() is [%s]", request.GET.dict())

        if uuid1:
            url = micro_url + '/<uuid1>'
            queryset = URL.objects.filter(apiserver_url=url).filter(active=True)
            #queryset = URL.objects.filter(apiserver_url__icontains=micro_url).filter(active=True)
        else:
            queryset = URL.objects.filter(apiserver_url=micro_url).filter(active=True) 

        passes, response = _passes_basic_checks(request, queryset, micro_url)

        if not passes:
            return response

        return build_api_response(request=request, qs=queryset, url=micro_url, uuid1=uuid1)

# -----------------------------------------------------------------------------

def _passes_basic_checks(request, queryset, url):

    if queryset.count() == 0:
        #return False, Response(status=status.HTTP_404_NOT_FOUND)
        message = { 'message': 'Nowt found', 'request_url': request.path }
        return False, Response(message, status=status.HTTP_404_NOT_FOUND)

    if request.content_type != "application/json":
        message = { 'message': 'Incorrect Content-Type header - JSON only allowed' }
        return False, Response(message, status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    dict1 = queryset.values('methods').get()
    methods = dict1.get('methods')

    if request.method not in methods:
        message = { 'message': 'Unsuitable method for this url' }
        return False, Response(message, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    proto_header = request.headers.get('X-Forwarded-Proto')

    if proto_header != "HTTPS" and proto_header != "https":
        message = { 'message': 'You must use https' }
        return False, Response(message, status=status.HTTP_406_NOT_ACCEPTABLE)

    # if we can't determine the originating ip address then reject
    if not 'HTTP_X_REAL_IP' in request.META:
        message = { 'message': 'Dunno where you live so you\'re not coming in' }
        return False, Response(message, status=status.HTTP_400_BAD_REQUEST)
    else:
        # if exists check against our ip limiting if it's switched on for this url
        ip_restrictions = queryset.values('ip_address_limiter').get()
        limit_ip = queryset.values('limit_ip').get()
        if limit_ip.get('limit_ip'):
            message = { 'message': 'You\'re from a dodgy part of town' }
            if ip_restrictions.get('ip_address_limiter') != "":
                good_ips = json.loads(ip_restrictions.get('ip_address_limiter'))
                if not request.META.get('HTTP_X_REAL_IP') in good_ips:
                    logger.debug("HTTP_X_REAL_IP is [%s]", request.META.get('HTTP_X_REAL_IP'))
                    return False, Response(message, status=status.HTTP_403_FORBIDDEN)
            else:
                return False, Response(message, status=status.HTTP_403_FORBIDDEN)

    return True, None

