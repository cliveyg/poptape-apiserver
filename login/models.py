from django.db import models
from multiselectfield import MultiSelectField
from apiserver.validators import validate_apiserver_url, validate_login_url

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
    login_api_url = models.CharField(max_length=400, blank=False, unique=True, validators=[validate_login_url])
    ip_address_limiter = models.TextField(blank=True, null=True)
    access_level = models.IntegerField(default=10)
    active = models.BooleanField(default=True)
    methods = MultiSelectField(choices=HTTPMethod.METHOD_CHOICES, null=True, max_length=20)
    owner = models.ForeignKey('auth.User',
                              related_name='URL',
                              on_delete=models.PROTECT) 
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        """A string representation of the model."""
        return self.apiserver_url+" -> "+self.login_api_url

