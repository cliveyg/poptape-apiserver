# apiserver URL Configuration


from django.contrib import admin
from django.urls import path, re_path, include
from apiserver.views import StatusView, AllStatusView

urlpatterns = [
    path('apiserver/admin/', admin.site.urls),
    path('apiserver/status', StatusView.as_view(), name="status"),
    path('apiserver/status/all', AllStatusView.as_view(), name="allstatus"),
    re_path(r'^', include('dispatcher.urls')),
    # url(r'^api-auth/', include('rest_framework.urls'))
    # url(r'^.*$',Error404.as_view(), name='error404')
]
