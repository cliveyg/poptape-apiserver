# dispatcher URL Configuration
from django.urls import path, re_path, include
from rest_framework.urlpatterns import format_suffix_patterns
from dispatcher.views import CreateView, GetMicroserviceData
from django.http import JsonResponse

def response_404_handler(request, exception=None):
        return JsonResponse({ 'message': 'Nowt found', 'request_url': request.path }, status=404)

handler404 = response_404_handler

urlpatterns = [
        # TODO: improve the url matching
        path('api/dispatcher/auth/', include('rest_framework.urls', namespace='rest_framework')),
        re_path(r'^api/dispatcher/urls/$', CreateView.as_view(), name="create"),
        path('api/<slug:micro_url>/<int:ca_int>', GetMicroserviceData.as_view(), name="micro_details"),
        path('api/<slug:micro_url>/<uuid:uuid1>/<slug:end_url>', GetMicroserviceData.as_view(), name="micro_details"),
        path('api/<slug:micro_url>/<uuid:uuid1>', GetMicroserviceData.as_view(), name="micro_details"),
        #path('api/<slug:micro_url>/<slug:slug1>', GetMicroserviceData.as_view(), name="micro_details"),
        re_path(r'^api/(?P<micro_url>.+)/?$', GetMicroserviceData.as_view(), name="micro_details"),
]

urlpatterns = format_suffix_patterns(urlpatterns)
