# apiserver URL Configuration

# from django.contrib import admin
# from django.conf.urls import url, include
from django.urls import path, re_path, include
from rest_framework.urlpatterns import format_suffix_patterns
# from dispatcher.views import CreateView, DetailsView, GetMicroserviceData
from dispatcher.views import CreateView, GetMicroserviceData
# from dispatcher.views import GetMicroURL, GetItemURL
# from reverse_proxy.views import ProxyView

urlpatterns = [
        # TODO: improve the url matching
        path('apiserver/dispatcher/auth/', include('rest_framework.urls', namespace='rest_framework')),
        re_path(r'^apiserver/dispatcher/urls/$', CreateView.as_view(), name="create"),
        # url(r'^apiserver/micro/(?P<micro_url>.+)/?$', GetMicroserviceData.as_view(), name="microservice"),
        # url(r'^(?P<micro_url>.+)/(?P<uuid>[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12})$', GetMicroURL.as_view(), name="micro_details"),
        # url(r'^(?P<micro_url>.+)/?$', GetMicroURL.as_view(), name="micro_details"),
        path('apiserver/<slug:micro_url>/<uuid:uuid1>', GetMicroserviceData.as_view(), name="micro_details"),
        #re_path(r'^(?P<micro_url>.+)/<uuid:ms_uuid1>', GetMicroserviceData.as_view(), name="micro_details"),
        re_path(r'^apiserver/(?P<micro_url>.+)/?$', GetMicroserviceData.as_view(), name="micro_details"),
        # url(r'^apiserver/item/(?P<micro_url>.+)$', GetItemURL.as_view(), name="item_details"),
        # url(r'^apiserver/item/(?P<micro_url>.+)$', GetItemURL.as_view(), name="owt_else"),
]

urlpatterns = format_suffix_patterns(urlpatterns)
