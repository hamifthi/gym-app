from django.db.models import Count, Sum
from django.test import TestCase
from django.conf import settings
from django.urls import reverse

from users.models import Person, Athlete, Coach, Day
from finance.models import Income, Expense

from utils_module.utils import google_recaptcha_verify, random_code

import os, jwt
from datetime import time, date, timedelta

class PersonRegisterTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        request_data = {
            'name': 'Hamed',
            'last_name': 'Fathi',
            'email': 'test@gmail.com',
            'password1': 'sthfortest',
            'password2': 'sthfortest'
        }
        return request_data

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/users/register/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('sign-up'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get('/users/register/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register.html')

    def test_google_recaptcha(self):
        response = self.client.post('/users/register/', {'g-recaptcha-response': ''})
        self.assertEqual(response.status_code, 429)
        self.assertEqual(
            response.context['error_message'].replace(' ', ''),
            'the captcha is not correct maybe you are robot? please enter the code correctly'.replace(' ', '')
        )

    def test_register_with_valid_data_form(self):
        data = PersonRegisterTest.setUpTestData()
        response = self.client.post('/users/register/', data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['message'], 'The activation link has been sent to your account')
    
    def test_register_with_invalid_data_form(self):
        response = self.client.post('/users/register/', {})
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.context['error_message'], 'Please solve the error and try again')

    def test_view_url_get_method(self):
        response = self.client.get('/users/register/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['message'], 'Welcome. Please fill out the fields and Sign Up')

    def test_activation_link_with_None_email_or_code(self):
        data = PersonRegisterTest.setUpTestData()
        self.client.post('/users/register/', data)
        user = Person.objects.first()
        response = self.client.get("/users/register/", {'email': '', 'code': ''})
        self.assertEqual(response.status_code, 422)
        self.assertEqual(
            response.context['error_message'], 'Your request doesn\'t have email or code or both of them'
        )

    def test_activation_link_with_None_email(self):
        data = PersonRegisterTest.setUpTestData()
        self.client.post('/users/register/', data)
        user = Person.objects.first()
        response = self.client.get("/users/register/", {'email': '', 'code': user.code})
        self.assertEqual(response.status_code, 422)
        self.assertEqual(
            response.context['error_message'], 'Your request doesn\'t have email or code or both of them'
        )

    def test_randomly_created_url_for_two_step_registration(self):
        data = PersonRegisterTest.setUpTestData()
        self.client.post('/users/register/', data)
        user = Person.objects.first()
        response = self.client.get("/users/register/", {'email': user.email, 'code': user.code})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['message'], 'Your account has been activated.')

    def test_registered_person_with_invalid_code(self):
        data = PersonRegisterTest.setUpTestData()
        self.client.post('/users/register/', data)
        user = Person.objects.first()
        response = self.client.get("/users/register/", {'email': user.email, 'code': random_code()})
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.context['error_message'], 'This code is invalid, please try again')
        self.assertTemplateUsed(response, 'register.html')

class AthleteRegisterTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        saturday = Day.objects.create(day='Saturday', number=1)
        sunday = Day.objects.create(day='Sunday', number=2)
        monday = Day.objects.create(day='Monday', number=3)
        person = Person.objects.create(
            name='hamed', last_name='fathi', email='hamed.fathi@gmail.com'
        )
        person.set_password('sthfortest')
        person.save()
        coach_person = Person.objects.create(name='hamid', last_name='fathi',
        email='hamid.fathi@gmail.com', password='sthelsefortest')
        coach = Coach.objects.create(
            age=58, sport_field='Crossfit', start_time=time(18, 00, 00), end_time=time(21, 00, 00),
            last_transaction = date.today(), transaction_amount=200000, user=coach_person
        )
        coach.days_of_week.set([saturday, sunday, monday])
        cls.request_data = {
            'age': 23,
            'sport_field': 'Crossfit',
            'days_of_week': [Day.objects.first().pk],
            'start_time': '19:00:00',
            'end_time': '20:30:00',
            'last_transaction': date.today(),
            'transaction_amount': 150000,
            'trainer': Coach.objects.first().pk
        }

    def test_view_url_exists_at_desired_location(self):
        login = self.client.login(email='hamed.fathi@gmail.com', password='sthfortest')
        response = self.client.get('/users/register/athlete/')
        self.assertEqual(response.status_code, 200)
           
    def test_view_url_accessible_by_name(self):
        login = self.client.login(email='hamed.fathi@gmail.com', password='sthfortest')
        response = self.client.get(reverse('register_athlete'))
        self.assertEqual(response.status_code, 200)
        
    def test_view_uses_correct_template(self):
        login = self.client.login(email='hamed.fathi@gmail.com', password='sthfortest')
        response = self.client.get(reverse('register_athlete'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register_athlete.html')

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('register_athlete'))
        self.assertRedirects(response, '/users/login/?next=/users/register/athlete/')

    def test_logged_in_uses_correct_template(self):
        login = self.client.login(email='hamed.fathi@gmail.com', password='sthfortest')
        response = self.client.get(reverse('register_athlete'))
        
        # Check our user is logged in
        self.assertEqual(str(response.context['user']), 'hamed_fathi')
        # Check that we got a response "success"
        self.assertEqual(response.status_code, 200)

        # Check we used correct template
        self.assertTemplateUsed(response, 'register_athlete.html')

    def test_google_recaptcha(self):
        login = self.client.login(email='hamed.fathi@gmail.com', password='sthfortest')
        response = self.client.post('/users/register/athlete/', {'g-recaptcha-response': ''})
        self.assertEqual(response.status_code, 429)
        self.assertEqual(
            response.context['error_message'].replace(' ', ''),
            'the captcha is not correct maybe you are robot? please enter the code correctly'.replace(' ', '')
        )
    
    def test_register_with_valid_data_form(self):
        data = AthleteRegisterTest.request_data
        login = self.client.login(email='hamed.fathi@gmail.com', password='sthfortest')
        response = self.client.post('/users/register/athlete/', data)
        user = Person.objects.first()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context['message'], 
            f'{user.name}_{user.last_name} now becomes an athlete in your gym'
        )

    def test_an_expense_submitted_after_athlete_register_in_gym(self):
        data = AthleteRegisterTest.request_data
        login = self.client.login(email='hamed.fathi@gmail.com', password='sthfortest')
        response = self.client.post('/users/register/athlete/', data)
        user = Person.objects.first()
        athlete = Athlete.objects.first()
        expense = Expense.objects.get(user=user)
        self.assertEqual(expense.details, 'user registration gym membership')
        self.assertEqual(athlete.transaction_amount, expense.amount)
        self.assertEqual(expense.user, user)

    def test_athlete_register_form_is_invalid(self):
        login = self.client.login(email='hamed.fathi@gmail.com', password='sthfortest')
        response = self.client.post('/users/register/athlete/', {})
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.context['error_message'], 'Please solve the error and try again')
        self.assertTemplateUsed('register_athlete.html')

    def test_an_athlete_cannot_register_twice(self):
        data = AthleteRegisterTest.request_data
        login = self.client.login(email='hamed.fathi@gmail.com', password='sthfortest')
        response = self.client.post('/users/register/athlete/', data)
        response = self.client.post('/users/register/athlete/', data)
        self.assertEqual(response.status_code, 403)
        user = response.context['user']
        self.assertEqual(
            response.context['message'].replace(' ', ''), 
            f'{user.name} you are an athlete and you can not become a(n) athlete again.'.replace(' ', ''))
        self.assertTemplateUsed(response, 'register.html')
    
    def test_an_athlete_cannot_become_a_coach(self):
        data = AthleteRegisterTest.request_data
        login = self.client.login(email='hamed.fathi@gmail.com', password='sthfortest')
        response = self.client.post('/users/register/athlete/', data)
        data.pop('trainer')
        response = self.client.post('/users/register/coach/', data)
        self.assertEqual(response.status_code, 403)
        user = response.context['user']
        self.assertEqual(
            response.context['message'].replace(' ', ''), 
            f'{user.name} you are an athlete and you can not become a(n) coach again.'.replace(' ', ''))
        self.assertTemplateUsed(response, 'register.html')

class CoachRegisterTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        saturday = Day.objects.create(day='Saturday', number=1)
        sunday = Day.objects.create(day='Sunday', number=2)
        monday = Day.objects.create(day='Monday', number=3)
        person = Person.objects.create(
            name='hamed', last_name='fathi', email='hamed.fathi@gmail.com'
        )
        person.set_password('sthfortest')
        person.save()
        cls.request_data = {
            'age': 35,
            'sport_field': 'Crossfit',
            'days_of_week': [Day.objects.first().pk],
            'start_time': '19:00:00',
            'end_time': '20:30:00',
            'last_transaction': date.today(),
            'transaction_amount': 2000000,
        }

    def test_view_url_exists_at_desired_location(self):
        login = self.client.login(email='hamed.fathi@gmail.com', password='sthfortest')
        response = self.client.get('/users/register/coach/')
        self.assertEqual(response.status_code, 200)
           
    def test_view_url_accessible_by_name(self):
        login = self.client.login(email='hamed.fathi@gmail.com', password='sthfortest')
        response = self.client.get(reverse('register_coach'))
        self.assertEqual(response.status_code, 200)
        
    def test_view_uses_correct_template(self):
        login = self.client.login(email='hamed.fathi@gmail.com', password='sthfortest')
        response = self.client.get(reverse('register_coach'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register_coach.html')
    
    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('register_coach'))
        self.assertRedirects(response, '/users/login/?next=/users/register/coach/')

    def test_logged_in_uses_correct_template(self):
        login = self.client.login(email='hamed.fathi@gmail.com', password='sthfortest')
        response = self.client.get(reverse('register_coach'))
        
        # Check our user is logged in
        self.assertEqual(str(response.context['user']), 'hamed_fathi')
        # Check that we got a response "success"
        self.assertEqual(response.status_code, 200)

        # Check we used correct template
        self.assertTemplateUsed(response, 'register_coach.html')

    def test_google_recaptcha(self):
        login = self.client.login(email='hamed.fathi@gmail.com', password='sthfortest')
        response = self.client.post('/users/register/coach/', {'g-recaptcha-response': ''})
        self.assertEqual(response.status_code, 429)
        self.assertEqual(
            response.context['error_message'].replace(' ', ''),
            'the captcha is not correct maybe you are robot? please enter the code correctly'.replace(' ', '')
        )
    
    def test_register_with_valid_data_form(self):
        data = CoachRegisterTest.request_data
        login = self.client.login(email='hamed.fathi@gmail.com', password='sthfortest')
        response = self.client.post('/users/register/coach/', data)
        user = Person.objects.first()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context['message'],
            f'{user.name}_{user.last_name} is a coach in your gym now'
        )

    def test_athlete_register_form_is_invalid(self):
        login = self.client.login(email='hamed.fathi@gmail.com', password='sthfortest')
        response = self.client.post('/users/register/coach/', {})
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.context['error_message'], 'Please solve the error and try again')
        self.assertTemplateUsed('register_coach.html')

    def test_a_coach_cannot_register_twice(self):
        data = CoachRegisterTest.request_data
        login = self.client.login(email='hamed.fathi@gmail.com', password='sthfortest')
        response = self.client.post('/users/register/coach/', data)
        response = self.client.post('/users/register/coach/', data)
        self.assertEqual(response.status_code, 403)
        user = response.context['user']
        self.assertEqual(
            response.context['message'].replace(' ', ''),
            f'{user.name} you are a coach and you can not become a(n) coach again.'.replace(' ', ''))
        self.assertTemplateUsed(response, 'register.html')

    def test_a_coach_cannot_become_an_athlete(self):
        data = CoachRegisterTest.request_data
        login = self.client.login(email='hamed.fathi@gmail.com', password='sthfortest')
        response = self.client.post('/users/register/coach/', data)
        response = self.client.post('/users/register/athlete/', data)
        self.assertEqual(response.status_code, 403)
        user = response.context['user']
        self.assertEqual(
            response.context['message'].replace(' ', ''), 
            f'{user.name} you are a coach and you can not become a(n) athlete again.'.replace(' ', ''))
        self.assertTemplateUsed(response, 'register.html')

class IndexTest(TestCase):
    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
           
    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        
    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')

class IncomeSubmitTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        person = Person.objects.create(
            name='hamed', last_name='fathi', email='hamed.fathi@gmail.com'
        )
        person.set_password('sthfortest')
        person.save()
        cls.request_data = {
            'details': 'this is for the test',
            'amount': 200000,
        }

    def test_view_url_exists_at_desired_location(self):
        login = self.client.login(email='hamed.fathi@gmail.com', password='sthfortest')
        response = self.client.get('/finance/submit/income/')
        self.assertEqual(response.status_code, 200)
           
    def test_view_url_accessible_by_name(self):
        login = self.client.login(email='hamed.fathi@gmail.com', password='sthfortest')
        response = self.client.get(reverse('submit_income'))
        self.assertEqual(response.status_code, 200)
        
    def test_view_uses_correct_template(self):
        login = self.client.login(email='hamed.fathi@gmail.com', password='sthfortest')
        response = self.client.get(reverse('submit_income'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'submit_income.html')

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('submit_income'))
        self.assertRedirects(response, '/users/login/?next=/finance/submit/income/')

    def test_logged_in_uses_correct_template(self):
        login = self.client.login(email='hamed.fathi@gmail.com', password='sthfortest')
        response = self.client.get(reverse('submit_income'))
        
        # Check our user is logged in
        self.assertEqual(str(response.context['user']), 'hamed_fathi')
        # Check that we got a response "success"
        self.assertEqual(response.status_code, 200)

        # Check we used correct template
        self.assertTemplateUsed(response, 'submit_income.html')
        
    def test_submit_an_income_successfuly(self):
        login = self.client.login(email='hamed.fathi@gmail.com', password='sthfortest')
        data = IncomeSubmitTest.request_data
        response = self.client.post('/finance/submit/income/', data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/')
    
    def test_submit_an_income_with_invalid_data_form(self):
        login = self.client.login(email='hamed.fathi@gmail.com', password='sthfortest')
        response = self.client.post('/finance/submit/income/', {})
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.context['error_message'], 'Please solve the error and try again')
        self.assertTemplateUsed('submit_income.html')

class ExpenseSubmitTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        person = Person.objects.create(
            name='hamed', last_name='fathi', email='hamed.fathi@gmail.com'
        )
        person.set_password('sthfortest')
        person.save()
        cls.request_data = {
            'details': 'this is for the test',
            'amount': 200000,
        }

    def test_view_url_exists_at_desired_location(self):
        login = self.client.login(email='hamed.fathi@gmail.com', password='sthfortest')
        response = self.client.get('/finance/submit/expense/')
        self.assertEqual(response.status_code, 200)
           
    def test_view_url_accessible_by_name(self):
        login = self.client.login(email='hamed.fathi@gmail.com', password='sthfortest')
        response = self.client.get(reverse('submit_expense'))
        self.assertEqual(response.status_code, 200)
        
    def test_view_uses_correct_template(self):
        login = self.client.login(email='hamed.fathi@gmail.com', password='sthfortest')
        response = self.client.get(reverse('submit_expense'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'submit_expense.html')

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('submit_expense'))
        self.assertRedirects(response, '/users/login/?next=/finance/submit/expense/')

    def test_logged_in_uses_correct_template(self):
        login = self.client.login(email='hamed.fathi@gmail.com', password='sthfortest')
        response = self.client.get(reverse('submit_expense'))
        
        # Check our user is logged in
        self.assertEqual(str(response.context['user']), 'hamed_fathi')
        # Check that we got a response "success"
        self.assertEqual(response.status_code, 200)

        # Check we used correct template
        self.assertTemplateUsed(response, 'submit_expense.html')
        
    def test_submit_an_expense_successfuly(self):
        login = self.client.login(email='hamed.fathi@gmail.com', password='sthfortest')
        data = ExpenseSubmitTest.request_data
        response = self.client.post('/finance/submit/expense/', data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/')
    
    def test_submit_an_expense_with_invalid_data_form(self):
        login = self.client.login(email='hamed.fathi@gmail.com', password='sthfortest')
        response = self.client.post('/finance/submit/expense/', {})
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.context['error_message'], 'Please solve the error and try again')
        self.assertTemplateUsed('submit_expense.html')

class TransactionReportFormTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        person = Person.objects.create(
            name='hamed', last_name='fathi', email='hamed.fathi@gmail.com'
        )
        person.set_password('sthfortest')
        person.save()
        Income.objects.create(details='sth fot test', amount=10000, user=person)
        Expense.objects.create(details='sth fot test', amount=10000, user=person)
        cls.request_data = {
            'report_choice': '',
            'from_date': date(2020, 3, 23).strftime('%d-%m-%Y'),
            'to_date': date(2020, 4, 24).strftime('%d-%m-%Y'),
        }

    def test_view_url_exists_at_desired_location(self):
        login = self.client.login(email='hamed.fathi@gmail.com', password='sthfortest')
        response = self.client.get('/finance/report/form/')
        self.assertEqual(response.status_code, 200)
           
    def test_view_url_accessible_by_name(self):
        login = self.client.login(email='hamed.fathi@gmail.com', password='sthfortest')
        response = self.client.get(reverse('report_form'))
        self.assertEqual(response.status_code, 200)
        
    def test_view_uses_correct_template(self):
        login = self.client.login(email='hamed.fathi@gmail.com', password='sthfortest')
        response = self.client.get(reverse('report_form'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'report_form.html')

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('report_form'))
        self.assertRedirects(response, '/users/login/?next=/finance/report/form/')

    def test_logged_in_uses_correct_template(self):
        login = self.client.login(email='hamed.fathi@gmail.com', password='sthfortest')
        response = self.client.get(reverse('report_form'))
        
        # Check our user is logged in
        self.assertEqual(str(response.context['user']), 'hamed_fathi')
        # Check that we got a response "success"
        self.assertEqual(response.status_code, 200)

        # Check we used correct template
        self.assertTemplateUsed(response, 'report_form.html')

    def test_view_redirected_to_income_report(self):
        data = TransactionReportFormTest.request_data
        data['report_choice'] = 'income'
        login = self.client.login(email='hamed.fathi@gmail.com', password='sthfortest')
        response = self.client.post('/finance/report/form/', data)
        self.assertRedirects(response, '/finance/report/income/')
    
    def test_view_redirected_to_expense_report(self):
        data = TransactionReportFormTest.request_data
        data['report_choice'] = 'expense'
        login = self.client.login(email='hamed.fathi@gmail.com', password='sthfortest')
        response = self.client.post('/finance/report/form/', data)
        self.assertRedirects(response, '/finance/report/expense/')
    
    def test_view_redirected_to_total_transaction_report(self):
        data = TransactionReportFormTest.request_data
        data['report_choice'] = 'total'
        login = self.client.login(email='hamed.fathi@gmail.com', password='sthfortest')
        response = self.client.post('/finance/report/form/', data)
        self.assertRedirects(response, '/finance/report/total/')

    def test_view_with_invalid_data_form(self):
        login = self.client.login(email='hamed.fathi@gmail.com', password='sthfortest')
        response = self.client.post('/finance/report/form/', {})
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.context['error_message'], 'Please solve the error and try again.')
        self.assertTemplateUsed(response, 'report_income.html')

class IncomeTransactionReportTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        person = Person.objects.create(
            name='hamed', last_name='fathi', email='hamed.fathi@gmail.com'
        )
        person.set_password('sthfortest')
        person.save()
        for i in range(10):
            Income.objects.create(details=f'this is for the test{i}', amount=2000, user=person)

    def test_view_url_exists_at_desired_location(self):
        login = self.client.login(email='hamed.fathi@gmail.com', password='sthfortest')
        response = self.client.get('/finance/report/income/')
        self.assertEqual(response.status_code, 200)
           
    def test_view_url_accessible_by_name(self):
        login = self.client.login(email='hamed.fathi@gmail.com', password='sthfortest')
        response = self.client.get(reverse('report_income'))
        self.assertEqual(response.status_code, 200)
        
    def test_view_uses_correct_template(self):
        login = self.client.login(email='hamed.fathi@gmail.com', password='sthfortest')
        response = self.client.get(reverse('report_income'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'report_income.html')
        
    def test_pagination_is_five(self):
        login = self.client.login(email='hamed.fathi@gmail.com', password='sthfortest')
        response = self.client.get(reverse('report_income'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'] == True)
        self.assertTrue(len(response.context['incomes']) == 5)

    def test_lists_all_incomes(self):
        # Get second page and confirm it has (exactly) remaining 5 items
        login = self.client.login(email='hamed.fathi@gmail.com', password='sthfortest')
        response = self.client.get(reverse('report_income')+'?page=2')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'] == True)
        self.assertTrue(len(response.context['incomes']) == 5)
    
    def test_report_with_from_and_to_date(self):
        login = self.client.login(email='hamed.fathi@gmail.com', password='sthfortest')
        session = self.client.session
        session['from_date'] = str(date.today() - timedelta(days=1))
        session.save()
        session['to_date'] = str(date.today() + timedelta(days=1))
        session.save()
        response = self.client.get(reverse('report_income'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'] == True)
        self.assertTrue(len(response.context['incomes']) == 5)

    def test_report_with_from_date(self):
        login = self.client.login(email='hamed.fathi@gmail.com', password='sthfortest')
        session = self.client.session
        session['from_date'] = str(date.today() - timedelta(days=1))
        session.save()
        response = self.client.get(reverse('report_income'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'] == True)
        self.assertTrue(len(response.context['incomes']) == 5)

class ExpenseTransactionReportTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        person = Person.objects.create(
            name='hamed', last_name='fathi', email='hamed.fathi@gmail.com'
        )
        person.set_password('sthfortest')
        person.save()
        for i in range(10):
            Expense.objects.create(details=f'this is for the test{i}', amount=2000, user=person)

    def test_view_url_exists_at_desired_location(self):
        login = self.client.login(email='hamed.fathi@gmail.com', password='sthfortest')
        response = self.client.get('/finance/report/expense/')
        self.assertEqual(response.status_code, 200)
           
    def test_view_url_accessible_by_name(self):
        login = self.client.login(email='hamed.fathi@gmail.com', password='sthfortest')
        response = self.client.get(reverse('report_expense'))
        self.assertEqual(response.status_code, 200)
        
    def test_view_uses_correct_template(self):
        login = self.client.login(email='hamed.fathi@gmail.com', password='sthfortest')
        response = self.client.get(reverse('report_expense'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'report_expense.html')
        
    def test_pagination_is_five(self):
        login = self.client.login(email='hamed.fathi@gmail.com', password='sthfortest')
        response = self.client.get(reverse('report_expense'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'] == True)
        self.assertTrue(len(response.context['expenses']) == 5)

    def test_lists_all_expenses(self):
        # Get second page and confirm it has (exactly) remaining 5 items
        login = self.client.login(email='hamed.fathi@gmail.com', password='sthfortest')
        response = self.client.get(reverse('report_expense')+'?page=2')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'] == True)
        self.assertTrue(len(response.context['expenses']) == 5)
    
    def test_report_with_from_and_to_date(self):
        login = self.client.login(email='hamed.fathi@gmail.com', password='sthfortest')
        session = self.client.session
        session['from_date'] = str(date.today() - timedelta(days=1))
        session.save()
        session['to_date'] = str(date.today() + timedelta(days=1))
        session.save()
        response = self.client.get(reverse('report_expense'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'] == True)
        self.assertTrue(len(response.context['expenses']) == 5)

    def test_report_with_from_date(self):
        login = self.client.login(email='hamed.fathi@gmail.com', password='sthfortest')
        session = self.client.session
        session['from_date'] = str(date.today() - timedelta(days=1))
        session.save()
        response = self.client.get(reverse('report_expense'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'] == True)
        self.assertTrue(len(response.context['expenses']) == 5)


class TotalTransactionReportTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        person = Person.objects.create(
            name='hamed', last_name='fathi', email='hamed.fathi@gmail.com'
        )
        person.set_password('sthfortest')
        person.save()
        for i in range(10):
            Income.objects.create(details=f'this is for the test{i}', amount=3000, user=person)
            Expense.objects.create(details=f'this is for the test{i}', amount=2000, user=person)

    def test_view_url_exists_at_desired_location(self):
        login = self.client.login(email='hamed.fathi@gmail.com', password='sthfortest')
        response = self.client.get('/finance/report/total/')
        self.assertEqual(response.status_code, 200)
           
    def test_view_url_accessible_by_name(self):
        login = self.client.login(email='hamed.fathi@gmail.com', password='sthfortest')
        response = self.client.get(reverse('total_transaction_report'))
        self.assertEqual(response.status_code, 200)
        
    def test_view_uses_correct_template(self):
        login = self.client.login(email='hamed.fathi@gmail.com', password='sthfortest')
        response = self.client.get(reverse('total_transaction_report'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'report_total.html')

    def test_report_with_from_and_to_date(self):
        login = self.client.login(email='hamed.fathi@gmail.com', password='sthfortest')
        session = self.client.session
        session['from_date'] = str(date.today() - timedelta(days=1))
        session.save()
        session['to_date'] = str(date.today() + timedelta(days=1))
        session.save()
        response = self.client.get(reverse('total_transaction_report'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('total' in response.context)
        self.assertTrue('incomes' in response.context)
        self.assertTrue('expenses' in response.context)

    def test_report_with_from_date(self):
        login = self.client.login(email='hamed.fathi@gmail.com', password='sthfortest')
        session = self.client.session
        session['from_date'] = str(date.today() - timedelta(days=1))
        session.save()
        response = self.client.get(reverse('total_transaction_report'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('total' in response.context)
        self.assertTrue('incomes' in response.context)
        self.assertTrue('expenses' in response.context)