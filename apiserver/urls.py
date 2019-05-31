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
from django.urls import path
from django.conf.urls import url, include
from apiserver.views import StatusView, AllStatusView

urlpatterns = [
    path('apiserver/admin/', admin.site.urls),
    path('apiserver/status', StatusView.as_view(), name="status"),
    path('apiserver/status/all', AllStatusView.as_view(), name="allstatus"),
    #path('apiserver/login/', include('login.urls')),
    url(r'^', include('dispatcher.urls')),
    #url(r'^api-auth/', include('rest_framework.urls'))
    #url(r'^.*$',Error404.as_view(), name='error404')
]
