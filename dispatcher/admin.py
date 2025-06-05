# dispatcher/admin.py
from django.contrib import admin
from . models import URL

admin.site.register(URL)

class FlatPageAdmin(admin.ModelAdmin):
    fields = ('apiserver_url', 'api_rules', 'access_level', 'methods',
              'limit_ip', 'ip_address_limiter', 'active', 'created', 'modified')

