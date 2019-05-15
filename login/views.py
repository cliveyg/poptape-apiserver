from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from rest_framework import generics

from .models import URL
from .serializers import LoginSerializer
from .response_builder import BuildAPIResponse

# get an instance of a logger
import logging
logger = logging.getLogger('apiserver')

# -----------------------------------------------------------------------------

class CreateView(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)

    # this class defines the create behavior of our rest api
    queryset = URL.objects.all()
    serializer_class = LoginSerializer

    def perform_create(self, serializer):
        # save the post data when creating a new url
        logger.info("CreateView:perform_create")
        serializer.save()


    def list(self, request, *args, **kwargs):
        logger.info("CreateView:list")
        queryset = self.filter_queryset(self.get_queryset())
        only_active_urls = queryset.filter(active=True)

        return Response(only_active_urls.values('apiserver_url', 'methods'), status=status.HTTP_200_OK)

# -----------------------------------------------------------------------------

class DetailsView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)

    # This class handles the http GET, PUT and DELETE requests.
    queryset = URL.objects.all()
    serializer_class = LoginSerializer

    def list(self, request, *args, **kwargs):
        #logger.info("DetailsView:list")
        queryset = self.filter_queryset(self.get_queryset())

        return Response(queryset.values(), status=status.HTTP_200_OK)

# -----------------------------------------------------------------------------

class GetLoginURL(generics.ListAPIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)

    # retrieves a model based on the inbound url

    serializer_class = LoginSerializer

    def get_queryset(self):
        # this view should return a single object based on the input url
        login_url = self.kwargs['login_url']
        #logger.debug("login url is [%s]", login_url)

        # only return the object if it's active
        url_model = URL.objects.filter(apiserver_url=login_url).filter(active=True)

        if url_model.count() == 0:
            logger.info("Nothing returned for URL [%s]", login_url)

        return url_model


    # override the list method so we can return a 404 if we need to

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        if queryset.count() == 0:
            return Response(status=status.HTTP_404_NOT_FOUND)

        # return a reduced set of the data for non-authenticated requests
        #if request.user.is_authenticated:
        #    return Response(queryset.values(), status=status.HTTP_200_OK)    
        #else:
        #    return Response(queryset.values('apiserver_url', 'methods'), status=status.HTTP_200_OK)

        #TODO: remove the above responses and pass through to somewhere else 
        # to build the correct response
        return BuildAPIResponse(request=request, qs=queryset)

# -----------------------------------------------------------------------------

