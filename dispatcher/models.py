from django.db import models
from multiselectfield import MultiSelectField
from apiserver.validators import validate_apiserver_url, validate_api_rules 
from apiserver.validators import validate_http_codes, validate_ip_addresses

class HTTPMethod(models.Model):
    id = models.AutoField(primary_key=True)
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
    class Meta:
        managed = True

    id = models.AutoField(primary_key=True)
    apiserver_url = models.CharField(max_length=400, blank=False,
                                     validators=[validate_apiserver_url])
    description = models.TextField(null=True, default='')
    api_rules = models.TextField(blank=False, null=False,
                                 validators=[validate_api_rules])
    access_level = models.IntegerField(default=99)
    active = models.BooleanField(default=True)
    methods = MultiSelectField(choices=HTTPMethod.METHOD_CHOICES, 
                               null=True, max_length=20)
    expected_successful_responses = models.CharField(max_length=50, blank=False, 
                                                     validators=[validate_http_codes])
    owner = models.ForeignKey('auth.User',
                              related_name='URL',
                              on_delete=models.PROTECT)
    limit_ip = models.BooleanField(default=True)
    ip_address_limiter = models.TextField(blank=True, null=True, 
                                          validators=[validate_ip_addresses])
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        """A string representation of the model."""
        active_str = ""
        if self.active:
            active_str = " - active"
        else:
            active_str = " - inactive"
        return self.apiserver_url+" ["+str(self.methods)+"] "+active_str

