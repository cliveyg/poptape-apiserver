from django.db import models
from multiselectfield import MultiSelectField
from apiserver.validators import validate_apiserver_url, validate_api_rules

class HTTPMethod(models.Model):
    GET = 'GET'
    PUT = 'PUT'
    DELETE = 'DELETE'
    POST = 'POST'
    METHOD_CHOICES = (
        (GET, 'GET'),
        (POST, 'POST'),
        (PUT, 'PUT'),
        (DELETE, 'DELETE'),
    )

# Create your models here.

class URL(models.Model):
    apiserver_url = models.CharField(max_length=400, blank=False, unique=True, validators=[validate_apiserver_url])
    api_rules = models.TextField(blank=False, null=False, unique=True, validators=[validate_api_rules])
    access_level = models.IntegerField(default=99)
    active = models.BooleanField(default=True)
    methods = MultiSelectField(choices=HTTPMethod.METHOD_CHOICES, null=True, max_length=20)
    owner = models.ForeignKey('auth.User',
                              related_name='URL',
                              on_delete=models.PROTECT) 
    ip_address_limiter = models.TextField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        """A string representation of the model."""
        active_str = ""
        if self.active:
            active_str = " [active]"
        else:
            active_str = " [inactive]"
        return self.apiserver_url+" . . . . . "+active_str

