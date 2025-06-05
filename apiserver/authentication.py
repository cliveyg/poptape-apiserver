# apiserver/authentication.py
from rest_framework.authentication import SessionAuthentication
import logging
logger = logging.getLogger('apiserver')

class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        logger.debug("In CsrfExemptSessionAuthentication - enforce_csrf")
        return True

