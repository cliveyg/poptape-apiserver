# /apiserver/tests.py
import json

from django.test import TestCase
from django.core.exceptions import ValidationError
from rest_framework.test import APIClient
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from django.urls import reverse
from django.conf import settings
import logging

# -----------------------------------------------------------------------------
# view test cases
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# test the api has url get capability

class ViewTestCase01(APITestCase):
    
    # test suite for the apiserver views

    def setUp(self):
        logging.disable(logging.CRITICAL)

    def test_api_can_get_a_url(self):
        
        # test the api can get a given url
        self.client = APIClient()

        url = reverse('status')
        response = self.client.get(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)


# -----------------------------------------------------------------------------
# test the api returns 404

class ViewTestCase02(APITestCase):

    # test suite for the api views

    def setUp(self):
        # define the test db record and any other test variables
        logging.disable(logging.CRITICAL)

    def test_api_returns_404(self):
        
        # test the api can get a given url
        self.client = APIClient()

        url = settings.APISERVER_SERVER + settings.APISERVER_URL + "wrongurl"
        response = self.client.get(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


# -----------------------------------------------------------------------------
# test the api returns correct code for unauthenticated user

class ViewTestCase03(APITestCase):

    # test suite for the api views

    def setUp(self):
        # define the test db record and any other test variables
        logging.disable(logging.CRITICAL)

    def test_api_returns_forbidden_if_not_auth(self):

        # test the api can get correct content for a given url
        self.client = APIClient()

        url = reverse('allstatus')
        response = self.client.get(url, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

# -----------------------------------------------------------------------------
# test the api returns list from /apiserver/status/all

class ViewTestCase04(APITestCase):

    # test suite for the api views

    def setUp(self):
        # define the test db record and any other test variables
        logging.disable(logging.CRITICAL)
        self.user = User.objects.create(username="clive")

    def test_api_returns_list_from_allstatus_if_authenticated(self):

        # test the api can get correct content for a given url
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        url = reverse('allstatus') 
        response = self.client.get(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
