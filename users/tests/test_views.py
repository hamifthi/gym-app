from django.test import TestCase
from django.urls import reverse
from users.models import Person
from users.views import google_recaptcha_verify
from django.conf import settings

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
        