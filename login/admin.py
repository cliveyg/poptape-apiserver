# login/admin.py
from django.contrib import admin
from . models import URL

admin.site.register(URL)

class FlatPageAdmin(admin.ModelAdmin):
    fields = ('apiserver_url', 'login_api_url', 'access_level', 'methods'
              'ip_address_limiter', 'active', 'created', 'modified')

