# /dispatcher/tests.py
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
import json

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
        self.apiserver_url = "api/login/status"
        self.description = "blah blah"
        self.api_rules = "[{ \"url\": \"authy/status\", \"pass_data\": false, \"fields\": [{\"message\": \"message\"}]}]"
        self.methods_list = ["GET"]

        self.test_url = URL(apiserver_url = self.apiserver_url,
                            api_rules = self.api_rules,
                            description = self.description,
                            access_level = 10,
                            owner = user,
                            limit_ip = False,
                            ip_address_limiter = "",
                            active = True,
                            methods = self.methods_list)
        self.test_url.save()

    def test_api_can_get_a_url(self):
        
        # test the api can get a given url
        self.client = APIClient()
        self.client.credentials(HTTP_X_FORWARDED_PROTO='https', HTTP_X_REAL_IP='101.23.45.67')

        #url = reverse('details', args=[self.test_url.apiserver_url], kwargs=[url=self.test_url.apiserver_url])
        kwargs={'micro_url': self.apiserver_url}
        url = reverse('micro_details', kwargs=kwargs)
        header = {'HTTP-X-Forwarded-Proto': 'https'}
        response = self.client.get(url, 
                                   content_type='application/json', 
                                   format="json")

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

        #url = reverse('details', args=["apiserver/login/noexisty"])
        kwargs={'micro_url': 'apiserver/nopelogin/noexisty'}
        url = reverse('micro_details', kwargs=kwargs)
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
        self.apiserver_url = "api/login/status"
        self.description = "blah blah"
        self.api_rules = "[{ \"url\": \"authy/status\", \"pass_data\": false, \"fields\": [{\"message\": \"message\"}]}]"
        self.methods_list = ["GET"]

        self.test_url = URL(apiserver_url = self.apiserver_url,
                            api_rules = self.api_rules,
                            access_level = 10,
                            owner = user,
                            limit_ip = False,
                            ip_address_limiter = "",
                            active = True,
                            methods = self.methods_list)
        self.test_url.save()

    def test_api_returns_correct_content(self):

        # test the api can get correct content for a given url
        self.client = APIClient()
        self.client.credentials(HTTP_X_FORWARDED_PROTO='https', HTTP_X_REAL_IP='101.23.45.67')

        #url = reverse('details', args=["apiserver/login/status"])

        url = reverse('micro_details', kwargs={ 'micro_url': self.apiserver_url})
        response = self.client.get(url,
                                   headers={'X-Forwarded-Proto': 'https'},
                                   content_type='application/json',
                                   format="json")        
        content = json.loads(response.content.decode())
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(content.get('request_url'), '/apiserver/login/status')
        # check that no access_level field is returned - so we know correct data
        # return for unauthenticated call
        #self.assertEqual(content[0].get('access_level'), None)

# -----------------------------------------------------------------------------
# test the api returns list from /apiserver/dispatcher/urls/

class ViewTestCase04(APITestCase):

    # test suite for the api views

    def setUp(self):
        # define the test db record and any other test variables
        logging.disable(logging.CRITICAL)
        user = User.objects.create(username="clive")
        self.apiserver_url = "api/login/url1"
        self.api_rules = "[{ \"url\": \"url/number/1\", \"fields\": [\"one\"]}]"
        self.methods_list = ["GET", "POST"]

        self.test_url1 = URL(apiserver_url = self.apiserver_url,
                            api_rules = self.api_rules,
                            access_level = 10,
                            owner = user,
                            active = True,
                            methods = self.methods_list)
        self.test_url1.save()

        logging.disable(logging.CRITICAL)
        self.apiserver_url = "api/login/url2"
        self.api_rules = "[{ \"url\": \"url/number/2\", \"fields\": [\"one\"]}]"
        self.methods_list = ["GET"]

        self.test_url2 = URL(apiserver_url = self.apiserver_url,
                            api_rules = self.api_rules,
                            access_level = 10,
                            owner = user,
                            active = True,
                            methods = self.methods_list)
        self.test_url2.save()

        logging.disable(logging.CRITICAL)
        self.apiserver_url = "api/login/url3"
        self.api_rules = "[{ \"url\": \"url/number/3\", \"fields\": [\"one\"]}]"
        self.methods_list = ["GET", "DELETE"]

        self.test_url3 = URL(apiserver_url = self.apiserver_url,
                            api_rules = self.api_rules,
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
        self.apiserver_url = "api/login/status"
        self.api_rules = "[{ \"url\": \"authy/status\", \"fields\": [{\"message\": \"message\"}]}]"
        self.methods_list = ["GET", "POST"]

        self.test_url = URL(apiserver_url = self.apiserver_url,
                            api_rules = self.api_rules,
                            access_level = 10,
                            owner = self.user,
                            ip_address_limiter = "",
                            active = True,
                            methods = self.methods_list)
        self.test_url.save()

    def test_api_returns_correct_content_for_authenticated_user(self):

        # test the api can get correct content for a given url
        self.client = APIClient()
        self.client.credentials(HTTP_X_FORWARDED_PROTO='https', HTTP_X_REAL_IP='101.23.45.67')
        self.client.force_authenticate(user=self.user)

        url = reverse('micro_details', kwargs={ 'micro_url': self.apiserver_url})
        response = self.client.get(url,
                                   headers={'X-Forwarded-Proto': 'https'},
                                   content_type='application/json',
                                   format="json")
        content = json.loads(response.content.decode())

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(content.get('request_url'), '/apiserver/login/status')
        # authenticated user returns extra fields such as access_level
        #self.assertEqual(content.get(''), 10)

# -----------------------------------------------------------------------------
# test the api returns 201 for created url

class ViewTestCase06(APITestCase):

    # test suite for the api views

    def setUp(self):
        # define the test db record and any other test variables
        logging.disable(logging.CRITICAL)
        self.user = User.objects.create(username="clive")

    def test_api_returns_201_for_post(self):

        # test the api can get correct content for a given url
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.api_rules = "[{ \"url\": \"url/number/1\", \"fields\": [{\"one\":\"one\"}]}]"

        url = reverse('create')
        self.url_data = {'apiserver_url': 'api/login/testcreate',
                         'api_rules': self.api_rules,
                         'access_level': 10,
                         'active': True,
                         'ip_address_limiter': '',
                         'owner': self.user.id,
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
        self.apiserver_url = "api/login/status"
        self.api_rules = "[{ \"url\": \"url/number/1\", \"fields\": [{\"one\":\"one\"}]}]"
        self.methods_list = ["GET", "POST"]

        self.test_url = URL(apiserver_url = self.apiserver_url,
                            api_rules = self.api_rules,
                            access_level = 10,
                            owner = self.user,
                            active = True,
                            methods = self.methods_list)
        self.test_url.save()

    def test_api_doesnt_allow_duplicates(self):

        # test the api can get correct content for a given url
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.api_rules = "[{ \"url\": \"url/number/1\", \"fields\": [{\"one\":\"one\"}]}]"

        url = reverse('create')
        self.url_data = {'apiserver_url': 'api/login/status',
                         'api_rules': self.api_rules,
                         'access_level': 10,
                         'active': True,
                         'ip_address_limiter': '',
                         'owner': self.user.id,
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
        self.api_rules = "[{ \"url\": \"url/number/1\", \"fields\": [{\"one\":\"one\"}]}]"

    def test_api_doesnt_allow_unauth_post(self):

        # test the api can get correct content for a given url
        self.client = APIClient()

        url = reverse('create')
        self.url_data = {'apiserver_url': 'api/login/status',
                         'api_rules': self.api_rules,
                         'access_level': 10,
                         'active': True,
                         'ip_address_limiter': '',
                         'owner': 1,
                         'methods': ('GET')}
        response = self.client.post(url, self.url_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
