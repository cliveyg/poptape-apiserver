# /login/tests.py
import json

from django.test import TestCase
from django.core.exceptions import ValidationError
from rest_framework.test import APIClient
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from django.urls import reverse
from ..models import URL
import logging

# -----------------------------------------------------------------------------
# view test cases
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# test the api has url get capability

class ViewTestCase01(APITestCase):
    
    # test suite for the api views

    def setUp(self):
        logging.disable(logging.CRITICAL)
        # define the test db record and any other test variables
        user = User.objects.create(username="clive")
        self.apiserver_url = "apiserver/login/status"
        self.login_api_url = "login/status"
        self.methods_list = ["GET", "POST"]

        self.test_url = URL(apiserver_url = self.apiserver_url,
                            login_api_url = self.login_api_url,
                            access_level = 10,
                            owner = user,
                            active = True,
                            methods = self.methods_list)
        self.test_url.save()

    def test_api_can_get_a_url(self):
        
        # test the api can get a given url
        self.client = APIClient()

        url = reverse('details', args=[self.test_url.apiserver_url])
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

        url = reverse('details', args=["apiserver/login/noexisty"])
        response = self.client.get(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


# -----------------------------------------------------------------------------
# test the api returns correct content for unauthenticated user

class ViewTestCase03(APITestCase):

    # test suite for the api views

    def setUp(self):
        # define the test db record and any other test variables
        logging.disable(logging.CRITICAL)
        user = User.objects.create(username="clive")
        self.apiserver_url = "apiserver/login/status"
        self.login_api_url = "login/status"
        self.methods_list = ["GET", "POST"]

        self.test_url = URL(apiserver_url = self.apiserver_url,
                            login_api_url = self.login_api_url,
                            access_level = 10,
                            owner = user,
                            active = True,
                            methods = self.methods_list)
        self.test_url.save()

    def test_api_returns_correct_content(self):

        # test the api can get correct content for a given url
        self.client = APIClient()

        url = reverse('details', args=["apiserver/login/status"])
        response = self.client.get(url, format="json")
        content = json.loads(response.content.decode())
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(content[0].get('apiserver_url'), 'apiserver/login/status')
        self.assertEqual(content[0].get('methods'), ["GET", "POST"])
        # check that no access_level field is returned - so we know correct data
        # return for unauthenticated call
        self.assertEqual(content[0].get('access_level'), None)

# -----------------------------------------------------------------------------
# test the api returns list from /apiserver/login/urls/

class ViewTestCase04(APITestCase):

    # test suite for the api views

    def setUp(self):
        # define the test db record and any other test variables
        logging.disable(logging.CRITICAL)
        user = User.objects.create(username="clive")
        self.apiserver_url = "apiserver/login/url1"
        self.login_api_url = "login/url1"
        self.methods_list = ["GET", "POST"]

        self.test_url1 = URL(apiserver_url = self.apiserver_url,
                            login_api_url = self.login_api_url,
                            access_level = 10,
                            owner = user,
                            active = True,
                            methods = self.methods_list)
        self.test_url1.save()

        logging.disable(logging.CRITICAL)
        self.apiserver_url = "apiserver/login/url2"
        self.login_api_url = "login/url2"
        self.methods_list = ["GET"]

        self.test_url2 = URL(apiserver_url = self.apiserver_url,
                            login_api_url = self.login_api_url,
                            access_level = 10,
                            owner = user,
                            active = True,
                            methods = self.methods_list)
        self.test_url2.save()

        logging.disable(logging.CRITICAL)
        self.apiserver_url = "apiserver/login/url3"
        self.login_api_url = "login/url3"
        self.methods_list = ["GET", "DELETE"]

        self.test_url3 = URL(apiserver_url = self.apiserver_url,
                            login_api_url = self.login_api_url,
                            access_level = 10,
                            owner = user,
                            active = True,
                            methods = self.methods_list)
        self.test_url3.save()

    def test_api_returns_list_from_urls_url(self):

        # test the api can get correct content for a given url
        self.client = APIClient()

        url = reverse('create') 
        response = self.client.get(url, format="json")
        content = json.loads(response.content.decode())

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(content), 3)

# -----------------------------------------------------------------------------
# test the api returns correct content for authenticated user

class ViewTestCase05(APITestCase):

    # test suite for the api views

    def setUp(self):
        # define the test db record and any other test variables
        logging.disable(logging.CRITICAL)
        self.user = User.objects.create(username="clive")
        self.apiserver_url = "apiserver/login/status"
        self.login_api_url = "login/status"
        self.methods_list = ["GET", "POST"]

        self.test_url = URL(apiserver_url = self.apiserver_url,
                            login_api_url = self.login_api_url,
                            access_level = 10,
                            owner = self.user,
                            active = True,
                            methods = self.methods_list)
        self.test_url.save()

    def test_api_returns_correct_content_for_authenticated_user(self):

        # test the api can get correct content for a given url
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        url = reverse('details', args=["apiserver/login/status"])
        response = self.client.get(url, format="json")
        content = json.loads(response.content.decode())

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(content[0].get('apiserver_url'), 'apiserver/login/status')
        self.assertEqual(content[0].get('methods'), ["GET", "POST"])
        # authenticated user returns extra fields such as access_level
        self.assertEqual(content[0].get('access_level'), 10)

# -----------------------------------------------------------------------------
# test the api returns 201 for created url

class ViewTestCase06(APITestCase):

    # test suite for the api views

    def setUp(self):
        # define the test db record and any other test variables
        #logging.disable(logging.CRITICAL)
        self.user = User.objects.create(username="clive")

    def test_api_returns_201_for_post(self):

        # test the api can get correct content for a given url
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        url = reverse('create')
        self.url_data = {'apiserver_url': 'apiserver/login/testcreate',
                         'login_api_url': 'login/testcreate',
                         'access_level': 10,
                         'active': True,
                         'ip_address_limiter': '',
                         'owner': 1,
                         'methods': ('GET')}
        response = self.client.post(url, self.url_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

# -----------------------------------------------------------------------------
# test the api won't allow a duplicate entry via post

class ViewTestCase07(APITestCase):

    # test suite for the api views

    def setUp(self):
        # define the test db record and any other test variables
        logging.disable(logging.CRITICAL)
        self.user = User.objects.create(username="clive")
        self.apiserver_url = "apiserver/login/status"
        self.login_api_url = "login/status"
        self.methods_list = ["GET", "POST"]

        self.test_url = URL(apiserver_url = self.apiserver_url,
                            login_api_url = self.login_api_url,
                            access_level = 10,
                            owner = self.user,
                            active = True,
                            methods = self.methods_list)
        self.test_url.save()

    def test_api_doesnt_allow_duplicates(self):

        # test the api can get correct content for a given url
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        url = reverse('create')
        self.url_data = {'apiserver_url': 'apiserver/login/status',
                         'login_api_url': 'login/testcreate',
                         'access_level': 10,
                         'active': True,
                         'ip_address_limiter': '',
                         'owner': 1,
                         'methods': ('GET')}        
        response = self.client.post(url, self.url_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

# -----------------------------------------------------------------------------
# test the api won't allow unauthenticated post

class ViewTestCase08(APITestCase):

    # test suite for the api views

    def setUp(self):
        # define the test db record and any other test variables
        logging.disable(logging.CRITICAL)

    def test_api_doesnt_allow_unauth_post(self):

        # test the api can get correct content for a given url
        self.client = APIClient()

        url = reverse('create')
        self.url_data = {'apiserver_url': 'apiserver/login/status',
                         'login_api_url': 'login/testcreate',
                         'access_level': 10,
                         'active': True,
                         'ip_address_limiter': '',
                         'owner': 1,
                         'methods': ('GET')}
        response = self.client.post(url, self.url_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
