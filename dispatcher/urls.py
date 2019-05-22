"""apiserver URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf.urls import url, include
from rest_framework.urlpatterns import format_suffix_patterns
from dispatcher.views import Error404, CreateView, DetailsView, GetMicroURL, GetItemURL, GetLoginURL, GetUserURL
from reverse_proxy.views import ProxyView

urlpatterns = [
        url(r'^apiserver/dispatcher/auth/', include('rest_framework.urls', namespace='rest_framework')),
        url(r'^apiserver/dispatcher/urls/$', CreateView.as_view(), name="create"),
        ##### url(r'^(?P<micro_url>.+)$', GetMicroURL.as_view(), name="details"),
        #url(r'^apiserver/login/(?P<micro_url>.+)/(?P<uuid>[0-9a-f-]+)$', GetLoginURL.as_view(), name="log_details"),
        url(r'^apiserver/login/(?P<micro_url>.+)$', GetLoginURL.as_view(), name="details"),
       # #url(r'^(?P<micro_url>.+)/(?P<uuid>[0-9a-f-]+)$', GetUserURL.as_view(), name="user_details"),
        url(r'^(?P<micro_url>.+)/(?P<uuid>[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12})$', GetUserURL.as_view(), name="user_details"), 
        url(r'^(?P<micro_url>.+)/?$', GetUserURL.as_view(), name="user_details"), 
        url(r'^apiserver/item/(?P<micro_url>.+)$', GetItemURL.as_view(), name="item_details"),        
        url(r'^apiserver/item/(?P<micro_url>.+)$', GetItemURL.as_view(), name="owt_else"),
        #url(r'^apiserver/user/(?P<micro_url>.+)/(?P<uuid>[0-9a-f-]+)$', GetUserURL.as_view(), name="user_details"),
        #url(r'^apiserver/item/(?P<micro_url>.+)$', GetItemURL.as_view(), name="item_details"),
        #url(r'^(?P<micro_url>.+)$', GetMicroURL.as_view(), name="micro_details"),
        #url(r'^(?P<login_url>.+)$', csrf_exempt(GetLoginURL.as_view()), name="details"),
        #url(r'^(?P<testy_url>.+)/$', DetailsView.as_view(), name="testy"),
        url(r'^.*$',Error404.as_view(), name='error404')
]

urlpatterns = format_suffix_patterns(urlpatterns)

