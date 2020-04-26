from django.utils.timezone import now
from django.test import TestCase

from users.models import Person, Day, Coach, Athlete
from finance.models import Income, Expense
from datetime import time, date
# Create your tests here.
class PersonModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Person.objects.create(name='hamed', last_name='fathi', email='hamed.fathi@gmail.com',
        password='sthfortest')

    def test_person_creation(self):
        person = Person.objects.get(id=1)
        self.assertTrue(isinstance(person, Person))

    def test_person_name_label(self):
        person = Person.objects.get(id=1)
        field_label = person._meta.get_field('name').verbose_name
        self.assertEqual(field_label, 'name')
    
    def test_person_last_name_label(self):
        person = Person.objects.get(id=1)
        field_label = person._meta.get_field('last_name').verbose_name
        self.assertEqual(field_label, 'last name')
    
    def test_person_email_label(self):
        person = Person.objects.get(id=1)
        field_label = person._meta.get_field('email').verbose_name
        self.assertEqual(field_label, 'Email Address')

    def test_person_name_max_length(self):
        person = Person.objects.get(id=1)
        max_length = person._meta.get_field('name').max_length
        self.assertEqual(max_length, 200)
    
    def test_person_last_name_max_length(self):
        person = Person.objects.get(id=1)
        max_length = person._meta.get_field('last_name').max_length
        self.assertEqual(max_length, 200)

    def test_object_name_is_name_underscore_last_name(self):
        person = Person.objects.get(id=1)
        expected_object_name = f'{person.name}_{person.last_name}'
        self.assertEqual(str(person), expected_object_name)

class DayModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Day.objects.create(day='Saturday', number=1)

    def test_day_creation(self):
        day = Day.objects.get(id=1)
        self.assertTrue(isinstance(day, Day))

    def test_day_day_label_name(self):
        day = Day.objects.get(id=1)
        field_label = day._meta.get_field('day').verbose_name
        self.assertEqual(field_label, 'day')

    def test_day_number_label_name(self):
        day = Day.objects.get(id=1)
        field_label = day._meta.get_field('number').verbose_name
        self.assertEqual(field_label, 'number')

    def test_object_name_is_day(self):
        day = Day.objects.get(id=1)
        expected_object_name = f'{day.day}'
        self.assertEqual(expected_object_name, str(day))

    def test_day_day_max_length(self):
        day = Day.objects.get(id=1)
        max_length = day._meta.get_field('day').max_length
        self.assertEqual(max_length, 9)

class CoachModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        person = Person.objects.create(name='hamed', last_name='fathi', email='hamed.fathi@gmail.com',
        password='sthfortest')
        saturday = Day.objects.create(day='Saturday', number=1)
        sunday = Day.objects.create(day='Sunday', number=2)
        monday = Day.objects.create(day='monday', number=3)
        coach = Coach.objects.create(
            age=23, sport_field='Crossfit', start_time=time(18, 00, 00), end_time=time(21, 00, 00),
            last_transaction = date.today(), transaction_amount=200000, user=person
            )
        coach.days_of_week.set([saturday, sunday, monday])

    def test_coach_creation(self):
        coach = Coach.objects.get(id=1)
        self.assertTrue(isinstance(coach, Coach))
    
    def test_coach_age_label(self):
        coach = Coach.objects.get(id=1)
        field_label = coach._meta.get_field('age').verbose_name
        self.assertEqual(field_label, 'age')
    
    def test_coach_sport_field_label(self):
        coach = Coach.objects.get(id=1)
        field_label = coach._meta.get_field('sport_field').verbose_name
        self.assertEqual(field_label, 'sport field')
    
    def test_coach_days_of_week_label(self):
        coach = Coach.objects.get(id=1)
        field_label = coach._meta.get_field('days_of_week').verbose_name
        self.assertEqual(field_label, 'days of week')
    
    def test_coach_start_time_label(self):
        coach = Coach.objects.get(id=1)
        field_label = coach._meta.get_field('start_time').verbose_name
        self.assertEqual(field_label, 'start time')
    
    def test_coach_end_time_label(self):
        coach = Coach.objects.get(id=1)
        field_label = coach._meta.get_field('end_time').verbose_name
        self.assertEqual(field_label, 'end time')
    
    def test_coach_last_transaction_label(self):
        coach = Coach.objects.get(id=1)
        field_label = coach._meta.get_field('last_transaction').verbose_name
        self.assertEqual(field_label, 'last_payment_of_salary')
    
    def test_coach_transaction_amount_label(self):
        coach = Coach.objects.get(id=1)
        field_label = coach._meta.get_field('transaction_amount').verbose_name
        self.assertEqual(field_label, 'salary')
    
    def test_coach_user_label(self):
        coach = Coach.objects.get(id=1)
        field_label = coach._meta.get_field('user').verbose_name
        self.assertEqual(field_label, 'user')
    
    def test_coach_sport_field_max_length(self):
        coach = Coach.objects.get(id=1)
        max_length = coach._meta.get_field('sport_field').max_length
        self.assertEqual(max_length, 12)
        
    def test_object_name_is_name_underscore_last_name(self):
        coach = Coach.objects.get(id=1)
        expected_object_name = f'{coach.user.name}_{coach.user.last_name}'
        self.assertEqual(expected_object_name, str(coach))

class AthleteModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        athlete_person = Person.objects.create(name='hamed', last_name='fathi', email='hamed.fathi@gmail.com',
        password='sthfortest')
        coach_person = Person.objects.create(name='hamid', last_name='fathi', email='hamid.fathi@gmail.com',
        password='sthfortest')
        saturday = Day.objects.create(day='Saturday', number=1)
        sunday = Day.objects.create(day='Sunday', number=2)
        monday = Day.objects.create(day='monday', number=3)
        coach = Coach.objects.create(
            age=58, sport_field='Crossfit', start_time=time(18, 00, 00), end_time=time(21, 00, 00),
            last_transaction = date.today(), transaction_amount=200000, user=coach_person
            )
        coach.days_of_week.set([saturday, sunday, monday])
        athlete = Athlete.objects.create(
            age=23, sport_field='Crossfit', start_time=time(18, 00, 00), end_time=time(21, 00, 00),
            last_transaction = date.today(), transaction_amount=150000, user=athlete_person,
            trainer=coach
            )
        athlete.days_of_week.set([saturday, sunday, monday])

    def test_athlete_creation(self):
        athlete = Athlete.objects.get(id=1)
        self.assertTrue(isinstance(athlete, Athlete))
    
    def test_athlete_age_label(self):
        athlete = Athlete.objects.get(id=1)
        field_label = athlete._meta.get_field('age').verbose_name
        self.assertEqual(field_label, 'age')
    
    def test_athlete_sport_field_label(self):
        athlete = Athlete.objects.get(id=1)
        field_label = athlete._meta.get_field('sport_field').verbose_name
        self.assertEqual(field_label, 'sport field')
    
    def test_athlete_days_of_week_label(self):
        athlete = Athlete.objects.get(id=1)
        field_label = athlete._meta.get_field('days_of_week').verbose_name
        self.assertEqual(field_label, 'days of week')
    
    def test_athlete_start_time_label(self):
        athlete = Athlete.objects.get(id=1)
        field_label = athlete._meta.get_field('start_time').verbose_name
        self.assertEqual(field_label, 'start time')
    
    def test_athlete_end_time_label(self):
        athlete = Athlete.objects.get(id=1)
        field_label = athlete._meta.get_field('end_time').verbose_name
        self.assertEqual(field_label, 'end time')
    
    def test_athlete_last_transaction_label(self):
        athlete = Athlete.objects.get(id=1)
        field_label = athlete._meta.get_field('last_transaction').verbose_name
        self.assertEqual(field_label, 'last_payment_of_membership')
    
    def test_athlete_transaction_amount_label(self):
        athlete = Athlete.objects.get(id=1)
        field_label = athlete._meta.get_field('transaction_amount').verbose_name
        self.assertEqual(field_label, 'gym_membership')

    def test_athlete_user_label(self):
        athlete = Athlete.objects.get(id=1)
        field_label = athlete._meta.get_field('user').verbose_name
        self.assertEqual(field_label, 'user')

    def test_athlete_sport_field_max_length(self):
        athlete = Athlete.objects.get(id=1)
        max_length = athlete._meta.get_field('sport_field').max_length
        self.assertEqual(max_length, 12)

    def test_object_name_is_name_underscore_last_name(self):
        athlete = Athlete.objects.get(id=1)
        expected_object_name = f'{athlete.user.name}_{athlete.user.last_name}'
        self.assertEqual(expected_object_name, str(athlete))

class IncomeModelTest(TestCase):
    @classmethod
    def setUpTestData(self):
        user = Person.objects.create(name='hamed', last_name='fathi', email='hamed.fathi@gmail.com',
        password='sthfortest')
        Income.objects.create(details='test', date=now(), amount=10000,
        user=user)

    def test_income_creation(self):
        income = Income.objects.get(id=1)
        self.assertTrue(isinstance(income, Income))

    def test_income_details_label_name(self):
        income = Income.objects.get(id=1)
        field_label = income._meta.get_field('details').verbose_name
        self.assertEqual(field_label, 'details')

    def test_income_date_label_name(self):
        income = Income.objects.get(id=1)
        field_label = income._meta.get_field('date').verbose_name
        self.assertEqual(field_label, 'date')

    def test_income_amount_label_name(self):
        income = Income.objects.get(id=1)
        field_label = income._meta.get_field('amount').verbose_name
        self.assertEqual(field_label, 'amount')
    
    def test_income_user_label_name(self):
        income = Income.objects.get(id=1)
        field_label = income._meta.get_field('user').verbose_name
        self.assertEqual(field_label, 'user')
    
    def test_income_code_label_name(self):
        income = Income.objects.get(id=1)
        field_label = income._meta.get_field('code').verbose_name
        self.assertEqual(field_label, 'code')

    def test_object_name_is_user_underscore_date_underscore_amount(self):
        income = Income.objects.get(id=1)
        expected_object_name = f'{income.user} {income.date} {income.amount} toman'
        self.assertEqual(expected_object_name, str(income))

class ExpenseModelTest(TestCase):
    @classmethod
    def setUpTestData(self):
        user = Person.objects.create(name='hamed', last_name='fathi', email='hamed.fathi@gmail.com',
        password='sthfortest')
        Expense.objects.create(details='test', date=now(), amount=10000,
        user=user)

    def test_expense_creation(self):
        expense = Expense.objects.get(id=1)
        self.assertTrue(isinstance(expense, Expense))

    def test_expense_details_label_name(self):
        expense = Expense.objects.get(id=1)
        field_label = expense._meta.get_field('details').verbose_name
        self.assertEqual(field_label, 'details')

    def test_expense_date_label_name(self):
        expense = Expense.objects.get(id=1)
        field_label = expense._meta.get_field('date').verbose_name
        self.assertEqual(field_label, 'date')

    def test_expense_amount_label_name(self):
        expense = Expense.objects.get(id=1)
        field_label = expense._meta.get_field('amount').verbose_name
        self.assertEqual(field_label, 'amount')
    
    def test_expense_user_label_name(self):
        expense = Expense.objects.get(id=1)
        field_label = expense._meta.get_field('user').verbose_name
        self.assertEqual(field_label, 'user')
    
    def test_expense_code_label_name(self):
        expense = Expense.objects.get(id=1)
        field_label = expense._meta.get_field('code').verbose_name
        self.assertEqual(field_label, 'code')

    def test_object_name_is_user_underscore_date_underscore_amount(self):
        expense = Expense.objects.get(id=1)
        expected_object_name = f'{expense.user} {expense.date} {expense.amount} toman'
        self.assertEqual(expected_object_name, str(expense))
