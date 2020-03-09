from django.test import TestCase
from django.urls import reverse
from users.models import Person, Token
from users.views import google_recaptcha_verify
from django.conf import settings
import os, binascii

class RegisterTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        request_data = {
            'name': 'Hamed',
            'last_name': 'Fathi',
            'email': 'test@gmail.com',
            'password': 'sthfortest',
        }
        return request_data

    def test_google_recapcha(self):
        data = RegisterTest.setUpTestData()
        data['requestcode'] = True
        response = self.client.post('/register/', data)
        self.assertEqual(response.status_code, 429)
        self.assertEqual(response.context['message'], 'the captcha is not correct maybe you are robot?\
                     please enter the code correctly')
        self.assertTemplateUsed(response, 'register.html')

    def test_duplicate_email(self):
        data = RegisterTest.setUpTestData()
        response1 = self.client.post('/register/', data)
        response2 = self.client.post('/register/', data)
        self.assertEqual(response2.status_code, 409)
        self.assertEqual(response2.context['message'], 'this email has used before, if this is your email go to forgot password\
                and change your password')
        self.assertTemplateUsed(response2, 'register.html')

    def test_regular_registration(self):
        data = RegisterTest.setUpTestData()
        response = self.client.post('/register/', data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['message'], 'The activation link has been sent to your account')
        self.assertTemplateUsed(response, 'register.html')

    def test_register_url_get_method(self):
        response = self.client.get('/register/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['message'], '')
        self.assertTemplateUsed(response, 'register.html')

    def test_activation_link_with_None_email_or_code(self):
        data = RegisterTest.setUpTestData()
        self.client.post('/register/', data)
        user = Person.objects.get(email='test@gmail.com')
        response = self.client.get(f"http://127.0.0.1:8000/register/?email=None&code=None")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.context['message'], 'Your request doesn\'t have email or code or both of them')
        self.assertTemplateUsed(response, 'register.html')

    def test_activation_link_with_None_email(self):
        data = RegisterTest.setUpTestData()
        self.client.post('/register/', data)
        user = Person.objects.get(email='test@gmail.com')
        response = self.client.get(f"http://127.0.0.1:8000/register/?email=None&code={user.code}")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.context['message'], 'Your request doesn\'t have email or code or both of them')
        self.assertTemplateUsed(response, 'register.html')

    def test_activation_link_with_None_code(self):
        data = RegisterTest.setUpTestData()
        self.client.post('/register/', data)
        user = Person.objects.get(email='test@gmail.com')
        response = self.client.get(f"http://127.0.0.1:8000/register/?email={user.email}&code=None")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.context['message'], 'Your request doesn\'t have email or code or both of them')
        self.assertTemplateUsed(response, 'register.html')

    def test_randomly_created_url_for_two_step_registration(self):
        data = RegisterTest.setUpTestData()
        self.client.post('/register/', data)
        user = Person.objects.get(email='test@gmail.com')
        response = self.client.get(f"http://127.0.0.1:8000/register/?email={user.email}&code={user.code}")
        token = Token.objects.get(user=user)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['message'], f'Your account has been activated please save your token is \
                    {token.token} because it will not show to you again')
        self.assertTemplateUsed(response, 'register.html')

    def test_unvalid_code(self):
        data = RegisterTest.setUpTestData()
        self.client.post('/register/', data)
        user = Person.objects.get(email='test@gmail.com')
        code = binascii.b2a_hex(os.urandom(28)).decode('utf-8')
        response = self.client.get(f"http://127.0.0.1:8000/register/?email={user.email}&code={code}")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.context['message'], f'This code is unvalid, please try again')
        self.assertTemplateUsed(response, 'register.html')