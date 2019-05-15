# /login/tests.py
import json

from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from rest_framework.test import APIClient
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from django.urls import reverse
from ..models import URL

# tests go here

# -----------------------------------------------------------------------------
# model test cases
# -----------------------------------------------------------------------------

class ModelTestCase01(TestCase):

    def setUp(self):
        # define the test client and other test variables
        user = User.objects.create(username="clive") 
        self.apiserver_url = "/apiserver/login/status"
        self.login_api_url = "/login/status"
        self.methods_list = ["GET", "POST"] 
        
        self.modeltest = URL(apiserver_url = self.apiserver_url,
                             login_api_url = self.login_api_url,
                             access_level = 10,
                             owner = user,
                             active = True,
                             methods = self.methods_list)

    def test_model_can_create_a_url_entry(self):
        """ test the URL model """
        old_count = URL.objects.count()
        self.modeltest.save()
        new_count = URL.objects.count()
        self.assertNotEqual(old_count, new_count)

# -----------------------------------------------------------------------------

class ModelTestCase02(TestCase):

    def setUp(self):
        # define the test client and other test variables
        user = User.objects.create(username="clive")
        self.apiserver_url = "apiserver/login/status"
        self.login_api_url = "login/status"
        self.methods_list = ["GET", "POST"]

        self.modeltest = URL(apiserver_url = self.apiserver_url,
                             login_api_url = self.login_api_url,
                             access_level = 10,
                             owner = user,
                             active = True,
                             methods = self.methods_list)

    def test_model_validates_url_entrys_1(self):
        """ test the URL model accepts correct prefixs for urls"""
        self.assertEqual(self.modeltest.full_clean(), None)

# -----------------------------------------------------------------------------
# test the URL model doesn't accept incorrect prefix for apiserver url

class ModelTestCase03(TestCase):

    def setUp(self):
        # define the test client and other test variables
        user = User.objects.create(username="clive")
        self.apiserver_url = "apiserver/login/status"
        self.login_api_url = "/login/status"
        self.methods_list = ["GET", "POST"]

        self.modeltest = URL(apiserver_url = self.apiserver_url,
                             login_api_url = self.login_api_url,
                             access_level = 10,
                             owner = user,
                             active = True,
                             methods = self.methods_list)

    def test_model_does_not_create_a_url_entry_1(self):
        with self.assertRaises(ValidationError) as valerr:
            self.modeltest.full_clean()

# -----------------------------------------------------------------------------
# test the URL model doesn't accept incorrect prefix for login url

class ModelTestCase04(TestCase):

    def setUp(self):
        # define the test client and other test variables
        user = User.objects.create(username="clive")
        self.apiserver_url = "/apiserver/login/status"
        self.login_api_url = "login/status"
        self.methods_list = ["GET", "POST"]

        self.modeltest = URL(apiserver_url = self.apiserver_url,
                             login_api_url = self.login_api_url,
                             access_level = 10,
                             owner = user,
                             active = True,
                             methods = self.methods_list)

    def test_model_does_not_create_a_url_entry_2(self):
        with self.assertRaises(ValidationError) as valerr:
            self.modeltest.full_clean()

# -----------------------------------------------------------------------------
# test the URL model doesn't accept incorrect http methods

class ModelTestCase05(TestCase):

    def setUp(self):
        # define the test client and other test variables
        user = User.objects.create(username="clive")
        self.apiserver_url = "apiserver/login/status"
        self.login_api_url = "login/status"
        self.methods_list = ["NOTACORRECTVERB"]

        self.modeltest = URL(apiserver_url = self.apiserver_url,
                             login_api_url = self.login_api_url,
                             access_level = 10,
                             owner = user,
                             active = True,
                             methods = self.methods_list)

    def test_model_does_not_create_a_url_entry_3(self):
        with self.assertRaises(ValidationError) as valerr:
            self.modeltest.full_clean()

# -----------------------------------------------------------------------------
# test the URL model doesn't accept non-numeric in access level

class ModelTestCase06(TestCase):

    def setUp(self):
        # define the test client and other test variables
        user = User.objects.create(username="clive")
        self.apiserver_url = "apiserver/login/status"
        self.login_api_url = "login/status"
        self.methods_list = ["PUT"]

        self.modeltest = URL(apiserver_url = self.apiserver_url,
                             login_api_url = self.login_api_url,
                             access_level = "not a number",
                             owner = user,
                             active = True,
                             methods = self.methods_list)

    def test_model_does_create_a_url_entry_4(self):
        with self.assertRaises(ValidationError) as valerr:
            self.modeltest.full_clean()

# -----------------------------------------------------------------------------
# test the URL model accepts all http methods

class ModelTestCase07(TestCase):

    def setUp(self):
        # define the test client and other test variables
        user = User.objects.create(username="clive")
        self.apiserver_url = "apiserver/login/status"
        self.login_api_url = "login/status"
        self.methods_list = ["POST", "GET", "PUT", "DELETE"]

        self.modeltest = URL(apiserver_url = self.apiserver_url,
                             login_api_url = self.login_api_url,
                             access_level = 10,
                             owner = user,
                             active = True,
                             methods = self.methods_list)

    def test_model_does_create_a_url_entry_2(self):
        self.assertEqual(self.modeltest.full_clean(), None)

# -----------------------------------------------------------------------------
# test the URL model rejects non-boolean for active flag

class ModelTestCase08(TestCase):

    def setUp(self):
        # define the test client and other test variables
        user = User.objects.create(username="clive")
        self.apiserver_url = "apiserver/login/status"
        self.login_api_url = "login/status"
        self.methods_list = ["POST", "GET", "PUT", "DELETE"]

        self.modeltest = URL(apiserver_url = self.apiserver_url,
                             login_api_url = self.login_api_url,
                             access_level = 10,
                             owner = user,
                             active = "Maybe",
                             methods = self.methods_list)

    def test_model_does_create_a_url_entry_5(self):
        with self.assertRaises(ValidationError) as valerr:
            self.modeltest.full_clean()

# -----------------------------------------------------------------------------
# test the URL model rejects none User class for owner

class ModelTestCase09(TestCase):

    def setUp(self):
        # define the test client and other test variables
        user = User.objects.create(username="clive")
        self.apiserver_url = "apiserver/login/status"
        self.login_api_url = "login/status"
        self.methods_list = ["POST", "GET", "PUT", "DELETE"]

    def test_model_does_not_create_a_url_entry_6(self):
        try:
            self.modeltest = URL(apiserver_url = self.apiserver_url,
                                 login_api_url = self.login_api_url,
                                 access_level = 10,
                                 owner = "badguy",
                                 active = True,
                                 methods = self.methods_list)
        except ValueError:
            self.assertRaises(ValueError)


# -----------------------------------------------------------------------------
# test the URL model rejects duplicate

class ModelTestCase10(TestCase):

    def setUp(self):
        # define the test client and other test variables
        user = User.objects.create(username="clive")
        self.apiserver_url = "apiserver/login/status"
        self.login_api_url = "login/status"
        self.methods_list = ["POST", "GET", "PUT", "DELETE"]

        self.modeltest1 = URL(apiserver_url = self.apiserver_url,
                             login_api_url = self.login_api_url,
                             access_level = 10,
                             owner = user,
                             active = True,
                             methods = self.methods_list)
        self.modeltest1.save()

        self.modeltest2 = URL(apiserver_url = self.apiserver_url,
                             login_api_url = self.login_api_url,
                             access_level = 10,
                             owner = user,
                             active = True,
                             methods = self.methods_list)

    def test_model_test_duplicate(self):
        with self.assertRaises(IntegrityError):
            self.modeltest2.save()
