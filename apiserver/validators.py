from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.conf import settings

# -----------------------------------------------------------------------------

def validate_apiserver_url(value):
    validate_url(value, settings.APISERVER_URL)

# -----------------------------------------------------------------------------
    
def validate_login_url(value):
    validate_url(value, settings.LOGIN_URL)

# -----------------------------------------------------------------------------

def validate_url(value, url):
    
    if isinstance(value, str) and (value.startswith(url) or value == "MULTIPLE"):
        pass
    else:
        raise ValidationError(
            _('URL doesn\'t start with the correct value'),
            params={'value': value},
        )

# _('%(value) doesn\'t start with the correct url'),        
# -----------------------------------------------------------------------------
