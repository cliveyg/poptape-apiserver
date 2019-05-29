from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
#from apiserver.csrfexemption import CsrfExemptSessionAuthentication
from rest_framework import status
from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework.generics import ListCreateAPIView, ListAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.views import APIView

from dispatcher.models import URL
from dispatcher.serializers import URLSerializer
from dispatcher.responder import BuildAPIResponse

from django.conf import settings

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

class GetMicroURL(ListAPIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    #authentication_classes = (CsrfExemptSessionAuthentication,)

    # retrieves a model based on the inbound url

    serializer_class = URLSerializer

    def dispatch(self, request, *args, **kwargs):
        return super(GetMicroURL, self).dispatch(request, *args, **kwargs)
    

    def get_queryset(self):
        # this view should return a single object based on the input url
        micro_url = self.kwargs['micro_url']

        # only return the object if it's active
        url_model = URL.objects.filter(apiserver_url=micro_url).filter(active=True)

        if url_model.count() == 0:
            logger.info("Nothing returned for URL [%s]", micro_url)

        return url_model


    # override the list method so we can return whatever status codes we need

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        if queryset.count() == 0:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if request.content_type != "application/json":
            message = { 'message': 'Incorrect Content-Type header - JSON only allowed' }
            return Response(message, status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

        dict1 = queryset.values('methods').get()
        methods = dict1.get('methods')

        if request.method not in methods:
            message = { 'message': 'Unsuitable method for this url' }
            return Response(message, status=status.HTTP_405_METHOD_NOT_ALLOWED)            

        proto_header = request.headers.get('X-Forwarded-Proto')

        if proto_header != "HTTPS" and proto_header != "https":
            message = { 'message': 'You must use https' }
            return Response(message, status=status.HTTP_406_NOT_ACCEPTABLE)

        # return a reduced set of the data for non-authenticated requests
        #if request.user.is_authenticated:
        #    return Response(queryset.values(), status=status.HTTP_200_OK)    
        #else:
        #    return Response(queryset.values('apiserver_url', 'methods'), status=status.HTTP_200_OK)

        #TODO: remove the above responses and pass through to somewhere else 
        # to build the correct response
        return BuildAPIResponse(request=request, qs=queryset)

# -----------------------------------------------------------------------------

class GetUserURL(ListAPIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)

    # retrieves a model based on the inbound url

    serializer_class = URLSerializer

    def dispatch(self, request, *args, **kwargs):
        return super(GetUserURL, self).dispatch(request, *args, **kwargs)


    def get_queryset(self):
        # 
        self.micro_url = self.kwargs['micro_url']

        if 'uuid' in self.kwargs:
            self.uuid = self.kwargs['uuid']
        else:
            self.uuid = None

        # only return the object if it's active and should only return exact match if there is not a uuid
        # in url
        if self.uuid:
            url_model = URL.objects.filter(apiserver_url__icontains=self.micro_url).filter(active=True)
        else:
            url_model = URL.objects.filter(apiserver_url=self.micro_url).filter(active=True)

        return url_model


    # override the list method so we can return whatever status codes we need

    def list(self, request, *args, **kwargs):

        #logger.info("In ya list")

        queryset = self.filter_queryset(self.get_queryset())

        passes, response = _passes_basic_checks(request, queryset, self.micro_url)

        if not passes:
            return response

        # we passed the basic checks so continue
        if self.uuid:
            return BuildAPIResponse(request=request, qs=queryset, url=self.micro_url, uuid=self.uuid)
        else:
            return BuildAPIResponse(request=request, qs=queryset, url=self.micro_url)



# -----------------------------------------------------------------------------

class GetLoginURL(ListAPIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    #authentication_classes = (CsrfExemptSessionAuthentication,)

    # retrieves a model based on the inbound url

    serializer_class = URLSerializer

    def dispatch(self, request, *args, **kwargs):
        return super(GetLoginURL, self).dispatch(request, *args, **kwargs)


    def get_queryset(self):
        # 
        micro_url = self.kwargs['micro_url']

        # only return the object if it's active
        url_model = URL.objects.filter(apiserver_url=micro_url).filter(active=True)

        if url_model.count() == 0:
            logger.info("Nothing returned for URL [%s]", micro_url)

        return url_model


    # override the list method so we can return whatever status codes we need

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        if queryset.count() == 0:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if request.content_type != "application/json":
            message = { 'message': 'Incorrect Content-Type header - JSON only allowed' }
            return Response(message, status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

        dict1 = queryset.values('methods').get()
        methods = dict1.get('methods')

        if request.method not in methods:
            message = { 'message': 'Unsuitable method for this url' }
            return Response(message, status=status.HTTP_405_METHOD_NOT_ALLOWED)

        proto_header = request.headers.get('X-Forwarded-Proto')

        if proto_header != "HTTPS" and proto_header != "https":
            message = { 'message': 'You must use https' }
            return Response(message, status=status.HTTP_406_NOT_ACCEPTABLE)

        # return a reduced set of the data for non-authenticated requests
        #if request.user.is_authenticated:
        #    return Response(queryset.values(), status=status.HTTP_200_OK)    
        #else:
        #    return Response(queryset.values('apiserver_url', 'methods'), status=status.HTTP_200_OK)

        #TODO: remove the above responses and pass through to somewhere else 
        # to build the correct response
        return BuildAPIResponse(request=request, qs=queryset)

# -----------------------------------------------------------------------------

class GetItemURL(ListAPIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    #authentication_classes = (CsrfExemptSessionAuthentication,)

    # retrieves a model based on the inbound url

    serializer_class = URLSerializer

# -----------------------------------------------------------------------------

class Error404(APIView):
    
    def get(self, request):
        return JsonResponse({ 'message': 'nowt ere mate' }, status=status.HTTP_404_NOT_FOUND)

# -----------------------------------------------------------------------------

def _passes_basic_checks(request, queryset, url):

    if queryset.count() == 0:
        return False, Response(status=status.HTTP_404_NOT_FOUND)

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
    
    return True, None

