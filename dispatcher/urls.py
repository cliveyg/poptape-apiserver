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
from .views import CreateView, DetailsView, GetMicroURL
from reverse_proxy.views import ProxyView
#from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
        url(r'^apiserver/dispatcher/auth/', include('rest_framework.urls', namespace='rest_framework')),
        url(r'^apiserver/dispatcher/urls/$', CreateView.as_view(), name="create"),
        #url(r'^apiserver/login(?P<login_url>.+)$', GetLoginURL.as_view(), name="details"),
        url(r'^(?P<micro_url>.+)$', GetMicroURL.as_view(), name="details"),
        #url(r'^(?P<login_url>.+)$', csrf_exempt(GetLoginURL.as_view()), name="details"),
        #url(r'^(?P<testy_url>.+)/$', DetailsView.as_view(), name="testy"),
]

urlpatterns = format_suffix_patterns(urlpatterns)

