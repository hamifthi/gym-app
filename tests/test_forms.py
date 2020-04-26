from django.test import TestCase
from django.contrib.auth.hashers import check_password

from users.models import Person, Coach, Athlete, Day
from users.forms import PersonCreationForm, CoachRegisterForm, AthleteRegisterForm

from finance.models import Income, Expense
from finance.forms import IncomeSubmitForm, ExpenseSubmitForm, ReportForm

from datetime import time, date

class PersonCreationFormTest(TestCase):
    def test_person_creation_form_is_valid(self):
        form = PersonCreationForm({
            'name': 'Hamed',
            'last_name': 'Fathi',
            'email': 'hamed.fathi@gmail.com',
            'password1': 'sthfortest',
            'password2': 'sthfortest'
        })
        self.assertTrue(form.is_valid())
        person = form.save()
        self.assertEqual(person.name, 'Hamed')
        self.assertEqual(person.last_name, 'Fathi')
        self.assertEqual(person.email, 'hamed.fathi@gmail.com')
        self.assertTrue(check_password('sthfortest', person.password))

    def test_person_creation_form_blank_data(self):
        form = PersonCreationForm({})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            'email': ['This field is required.'],
            'password1': ['This field is required.'],
            'password2': ['This field is required.'],
        })

    def test_person_creation_form_email_help_text_field(self):
        form = PersonCreationForm()
        self.assertEqual(form['email'].help_text, 'confirmation link will be sent to this address')

class CoachRegisterFormTest(TestCase):
    @classmethod
    def setUp(cls):
        Person.objects.create(name='hamed', last_name='fathi', email='hamed.fathi@gmail.com',
        password='sthfortest')
        Day.objects.create(day='Saturday', number=1)
        Day.objects.create(day='Sunday', number=2)
        Day.objects.create(day='Monday', number=3)

    def test_coach_creation_form_is_valid(self):
        form = CoachRegisterForm({
            'age': 23,
            'sport_field': 'Crossfit',
            'days_of_week': Day.objects.all(),
            'start_time': '19:00:00',
            'end_time': '20:30:00',
            'last_transaction': '2020-04-20',
            'transaction_amount': 2000000,
        })
        self.assertTrue(form.is_valid())
        coach = form.save(commit=False)
        coach.user = Person.objects.first()
        coach.save()
        coach.days_of_week.set(Day.objects.all())
        self.assertEqual(coach.age, 23)
        self.assertEqual(coach.sport_field, 'Crossfit')
        self.assertEqual(list(coach.days_of_week.all()), list(Day.objects.all()))
        self.assertEqual(coach.start_time, time(19, 00, 00))
        self.assertEqual(coach.end_time, time(20, 30, 00))
        self.assertEqual(coach.last_transaction, date(2020, 4, 20))
        self.assertEqual(coach.transaction_amount, 2000000)
        self.assertEqual(coach.user, Person.objects.first())

    def test_coach_creation_form_blank_data(self):
        form = CoachRegisterForm({})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            'age': ['This field is required.'],
            'sport_field': ['This field is required.'],
            'days_of_week': ['This field is required.'],
            'start_time': ['This field is required.'],
            'end_time': ['This field is required.'],
            'last_transaction': ['This field is required.'],
            'transaction_amount': ['This field is required.'],
        })

    def test_coach_creation_form_start_time_error_message(self):
        form = CoachRegisterForm({
            'age': 23,
            'sport_field': 'Crossfit',
            'days_of_week': Day.objects.all(),
            'start_time': '19.00.00',
            'end_time': '20:30:00',
            'last_transaction': '2020-04-20',
            'transaction_amount': 2000000,
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors['start_time'].get_json_data(escape_html=True)[0]['message'].replace(' ', ''),
            'Enter time in a correct format HH:mm:ss for instance:18:00:00'.replace(' ', '')
            )
    
    def test_coach_creation_form_end_time_error_message(self):
        form = CoachRegisterForm({
            'age': 23,
            'sport_field': 'Crossfit',
            'days_of_week': Day.objects.all(),
            'start_time': '19:00:00',
            'end_time': '20.30.00',
            'last_transaction': '2020-04-20',
            'transaction_amount': 2000000,
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors['end_time'].get_json_data(escape_html=True)[0]['message'].replace(' ', ''),
            'Enter time in a correct format HH:mm:ss for instance:19:30:00'.replace(' ', '')
            )

    def test_coach_creation_form_age_help_text_field(self):
        form = CoachRegisterForm()
        self.assertEqual(form['age'].help_text, 'Please enter your age here')
    
    def test_coach_creation_form_salary_help_text_field(self):
        form = CoachRegisterForm()
        self.assertEqual(form['transaction_amount'].help_text, 'Please enter your salary here')
    
    def test_coach_creation_form_start_time_help_text_field(self):
        form = CoachRegisterForm()
        self.assertEqual(form['start_time'].help_text, 'Work hour starting time')
    
    def test_coach_creation_form_end_time_help_text_field(self):
        form = CoachRegisterForm()
        self.assertEqual(form['end_time'].help_text, 'Work hour ending time')

class AthleteRegisterFormTest(TestCase):
    @classmethod
    def setUp(cls):
        coach_person = Person.objects.create(
            name='hamid', last_name='fathi', email='hamid.fathi@gmail.com', password='sthfortest'
        )
        saturday = Day.objects.create(day='Saturday', number=1)
        sunday = Day.objects.create(day='Sunday', number=2)
        monday = Day.objects.create(day='Monday', number=3)
        coach = Coach.objects.create(
            age=58, sport_field='Crossfit', start_time=time(18, 00, 00), end_time=time(21, 00, 00),
            last_transaction = date.today(), transaction_amount=200000, user=coach_person
        )
        coach.days_of_week.set([saturday, sunday, monday])

    def test_athlete_creation_form_is_valid(self):
        form = AthleteRegisterForm({
                'age': 23,
                'sport_field': 'Crossfit',
                'days_of_week': Day.objects.all(),
                'start_time': '19:00:00',
                'end_time': '20:30:00',
                'last_transaction': '2020-04-20',
                'transaction_amount': 150000,
                'trainer': Coach.objects.first()
            })
        self.assertTrue(form.is_valid())
        athlete = form.save(commit=False)
        athlete.user = Person.objects.first()
        athlete.save()
        athlete.days_of_week.set(Day.objects.all())
        self.assertEqual(athlete.age, 23)
        self.assertEqual(athlete.sport_field, 'Crossfit')
        self.assertEqual(list(athlete.days_of_week.all()), list(Day.objects.all()))
        self.assertEqual(athlete.start_time, time(19, 00, 00))
        self.assertEqual(athlete.end_time, time(20, 30, 00))
        self.assertEqual(athlete.last_transaction, date(2020, 4, 20))
        self.assertEqual(athlete.transaction_amount, 150000)
        self.assertEqual(athlete.user, Person.objects.first())
        self.assertEqual(athlete.trainer, Coach.objects.first())

    def test_athlete_creation_form_blank_data(self):
        form = AthleteRegisterForm({})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            'age': ['This field is required.'],
            'sport_field': ['This field is required.'],
            'days_of_week': ['This field is required.'],
            'start_time': ['This field is required.'],
            'end_time': ['This field is required.'],
            'last_transaction': ['This field is required.'],
            'transaction_amount': ['This field is required.'],
        })

    def test_athlete_creation_form_start_time_error_message(self):
        form = AthleteRegisterForm({
            'age': 23,
            'sport_field': 'Crossfit',
            'days_of_week': Day.objects.all(),
            'start_time': '19.00.00',
            'end_time': '20:30:00',
            'last_transaction': '2020-04-20',
            'transaction_amount': 2000000,
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors['start_time'].get_json_data(escape_html=True)[0]['message'].replace(' ', ''),
            'Enter time in a correct format HH:mm:ss for instance:18:00:00'.replace(' ', '')
            )
    
    def test_athlete_creation_form_end_time_error_message(self):
        form = AthleteRegisterForm({
            'age': 23,
            'sport_field': 'Crossfit',
            'days_of_week': Day.objects.all(),
            'start_time': '19:00:00',
            'end_time': '20.30.00',
            'last_transaction': '2020-04-20',
            'transaction_amount': 2000000,
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors['end_time'].get_json_data(escape_html=True)[0]['message'].replace(' ', ''),
            'Enter time in a correct format HH:mm:ss for instance:19:30:00'.replace(' ', '')
            )

    def test_athlete_creation_form_age_help_text_field(self):
        form = AthleteRegisterForm()
        self.assertEqual(form['age'].help_text, 'Please enter your age here')
    
    def test_athlete_creation_form_start_time_help_text_field(self):
        form = AthleteRegisterForm()
        self.assertEqual(form['start_time'].help_text, 'Training starting time')
    
    def test_athlete_creation_form_end_time_help_text_field(self):
        form = AthleteRegisterForm()
        self.assertEqual(form['end_time'].help_text, 'Training ending time')
    
    def test_athlete_creation_form_trainer_help_text_field(self):
        form = AthleteRegisterForm()
        self.assertEqual(form['trainer'].help_text, 'Which coach do you want to work with')

    def test_athlete_sport_field_is_different_from_coach(self):
        form = AthleteRegisterForm({
                'age': 23,
                'sport_field': 'Fitness',
                'days_of_week': Day.objects.all(),
                'start_time': '19:00:00',
                'end_time': '20:30:00',
                'last_transaction': '2020-04-20',
                'transaction_amount': 150000,
                'trainer': Coach.objects.first()
            })
        self.assertFalse(form.is_valid())
        coach = form.data['trainer']
        self.assertEqual(
            form.errors['sport_field'].get_json_data(escape_html=True)[0]['message'].replace(' ', ''),
            f'Your sport field and your coach sport field must be the same. Your\
                coach sport field is {coach.sport_field}'.replace(' ', '')
            )

    def test_athlete_days_of_week_is_different_from_coach(self):
        form = AthleteRegisterForm({
                'age': 23,
                'sport_field': 'Fitness',
                'days_of_week': [Day.objects.create(day='Tuesday', number=4)],
                'start_time': '19:00:00',
                'end_time': '20:30:00',
                'last_transaction': '2020-04-20',
                'transaction_amount': 150000,
                'trainer': Coach.objects.first()
            })
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors['days_of_week'].get_json_data(escape_html=True)[0]['message'],
            'Your coach goes to gym in different days'
            )
    
    def test_athlete_start_time_is_different_from_coach(self):
        form = AthleteRegisterForm({
                'age': 23,
                'sport_field': 'Fitness',
                'days_of_week': Day.objects.all(),
                'start_time': '17:00:00',
                'end_time': '20:30:00',
                'last_transaction': '2020-04-20',
                'transaction_amount': 150000,
                'trainer': Coach.objects.first()
            })
        self.assertFalse(form.is_valid())
        coach = form.data['trainer']
        self.assertEqual(
            form.errors['start_time'].get_json_data(escape_html=True)[0]['message'].replace(' ', ''),
            f'Your coach arrives at the gym later than this time. He or She arrives at\
                {coach.start_time}'.replace(' ', '')
            )
    
    def test_athlete_end_time_is_different_from_coach(self):
        form = AthleteRegisterForm({
                'age': 23,
                'sport_field': 'Fitness',
                'days_of_week': Day.objects.all(),
                'start_time': '19:00:00',
                'end_time': '21:30:00',
                'last_transaction': '2020-04-20',
                'transaction_amount': 150000,
                'trainer': Coach.objects.first()
            })
        self.assertFalse(form.is_valid())
        coach = form.data['trainer']
        self.assertEqual(
            form.errors['end_time'].get_json_data(escape_html=True)[0]['message'].replace(' ', ''),
            f'Your coach leaves the gym sooner than this time. He or She leaves at\
                {coach.end_time}'.replace(' ', '')
            )

class IncomeSubmitFormTest(TestCase):
    @classmethod
    def setUpTestData(self):
        Person.objects.create(name='hamed', last_name='fathi', email='hamed.fathi@gmail.com',
        password='sthfortest')

    def test_income_submit_form_is_valid(self):
        form = IncomeSubmitForm({
            'details': 'this is the test so there is nothing to say',
            'date': '2020-04-21',
            'amount': 10000
        })
        self.assertTrue(form.is_valid())
        income = form.save(commit=False)
        income.user = Person.objects.first()
        income.save()
        self.assertEqual(income.details, 'this is the test so there is nothing to say')
        self.assertEqual(income.date.strftime('%Y-%m-%d'), date(2020, 4, 21).strftime('%Y-%m-%d'))
        self.assertEqual(income.amount, 10000)
        self.assertEqual(income.user, Person.objects.first())

    def test_income_submit_form_blank_data(self):
        form = IncomeSubmitForm({})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            'details': ['This field is required.'],
            'amount': ['This field is required.'],
        })

    def test_income_Submit_form_details_help_text_field(self):
        form = IncomeSubmitForm()
        self.assertEqual(form['details'].help_text, 'Please describe how do you earn this income')
    
    def test_income_Submit_form_amount_help_text_field(self):
        form = IncomeSubmitForm()
        self.assertEqual(form['amount'].help_text, 'How much do you make?')
    
    def test_income_Submit_form_amount_error_message(self):
        form = IncomeSubmitForm({
            'details': 'this is the test so there is nothing to say',
            'date': '2020-04-21',
            'amount': 'sth'
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors['amount'].get_json_data(escape_html=True)[0]['message'].replace(' ', ''),
            'How much this is important. dont forget that'.replace(' ', '')
            )

class ExpenseSubmitFormTest(TestCase):
    @classmethod
    def setUpTestData(self):
        Person.objects.create(name='hamed', last_name='fathi', email='hamed.fathi@gmail.com',
        password='sthfortest')

    def test_expense_submit_form_is_valid(self):
        form = ExpenseSubmitForm({
            'details': 'this is the test so there is nothing to say',
            'date': '2020-04-21',
            'amount': 10000
        })
        self.assertTrue(form.is_valid())
        expense = form.save(commit=False)
        expense.user = Person.objects.first()
        expense.save()
        self.assertEqual(expense.details, 'this is the test so there is nothing to say')
        self.assertEqual(expense.date.strftime('%Y-%m-%d'), date(2020, 4, 21).strftime('%Y-%m-%d'))
        self.assertEqual(expense.amount, 10000)
        self.assertEqual(expense.user, Person.objects.first())

    def test_expense_submit_form_blank_data(self):
        form = ExpenseSubmitForm({})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            'details': ['This field is required.'],
            'amount': ['This field is required.'],
        })

    def test_expense_Submit_form_details_help_text_field(self):
        form = ExpenseSubmitForm()
        self.assertEqual(form['details'].help_text, 'Please describe how do you spend this money')
    
    def test_expense_Submit_form_amount_help_text_field(self):
        form = ExpenseSubmitForm()
        self.assertEqual(form['amount'].help_text, 'How much do you spend?')
    
    def test_expense_Submit_form_amount_error_message(self):
        form = ExpenseSubmitForm({
            'details': 'this is the test so there is nothing to say',
            'date': '2020-04-21',
            'amount': 'sth'
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors['amount'].get_json_data(escape_html=True)[0]['message'].replace(' ', ''),
            'How much this is important. dont forget that'.replace(' ', '')
            )

class ReportFormTest(TestCase):
    @classmethod
    def setUpTestData(self):
        Person.objects.create(name='hamed', last_name='fathi', email='hamed.fathi@gmail.com',
        password='sthfortest')

    def test_report_form_is_valid(self):
        form = ReportForm({
            'report_choice': 'income',
            'from_date': date(2020, 3, 21),
            'to_date': date(2020, 4, 21)
        })
        self.assertTrue(form.is_valid())


    def test_report_form_blank_data(self):
        form = ReportForm({})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            'report_choice': ['This field is required.'],
        })

    def test_report_form_report_choice_error(self):
        form = ReportForm({'report_choice': 'other_than_options'})
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors['report_choice'].get_json_data(escape_html=True)[0]['message'], 
            'Select a valid choice. other_than_options is not one of the available choices.',
        )

    def test_report_form_report_choice_help_text_field(self):
        form = ReportForm()
        self.assertEqual(form['report_choice'].help_text, 'Which one of transactions do you want to see?')
    
    def test_report_form_from_date_help_text_field(self):
        form = ReportForm()
        self.assertEqual(
            form['from_date'].help_text,
            'Please pick a from date to see transaction or leave blank to see all of your transactions'
            )
    
    def test_report_form_to_date_help_text_field(self):
        form = ReportForm()
        self.assertEqual(
            form['to_date'].help_text,
            'Please pick a from date to see transaction or leave blank to see all of your transactions'
            )