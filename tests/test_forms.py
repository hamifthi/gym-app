from django.test import TestCase
from django.contrib.auth.hashers import check_password

from users.forms import PersonCreationForm, CoachRegisterForm, AthleteRegisterForm
from users.models import Person, Coach, Athlete, Day

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