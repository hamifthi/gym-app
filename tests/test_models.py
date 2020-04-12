from django.test import TestCase

from users.models import Person
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
        self.assertEqual(field_label, 'last_name')
    
    def test_person_email_label(self):
        person = Person.objects.get(id=1)
        field_label = person._meta.get_field('email').verbose_name
        self.assertEqual(field_label, 'email')
    
    def test_person_code_label(self):
        person = Person.objects.get(id=1)
        field_label = person._meta.get_field('code').verbose_name
        self.assertEqual(field_label, 'code')

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
        self.assertEqual(expected_object_name, str(person))

class DayModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Day.objects.create(day='Saturday', number=1)

    def test_day_creation(self):
        day = Day.objects.get(id=1)
        self.assertTrue(isinstance(day, Day))

    def test_day_day_label_name(self):
        day = Day.objects.get(id=1)
        field_label = person._meta.get_field('day').verbose_name
        self.assertEqual(field_label, 'day')

    def test_day_number_label_name(self):
        day = Day.objects.get(id=1)
        field_label = person._meta.get_field('number').verbose_name
        self.assertEqual(field_label, 'number')

class CoachModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        person = Person.objects.create(name='hamed', last_name='fathi', email='hamed.fathi@gmail.com',
        password='sthfortest')
        saturday = Day.objects.create(day='Saturday', number=1)
        sunday = Day.objects.create(day='Sunday', number=2)
        monday = Day.objects.create(day='monday', number=3)
        Coach.objects.create(
            age=23, sport_field='Crossfit', days_of_week=[saturday, sunday, monday],
            start_time=time(18, 00, 00), end_time=time(21, 00, 00), last_transaction = date.today(),
            transaction_amount=200000, user=person
            )

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
        self.assertEqual(field_label, 'sport_field')
    
    def test_coach_days_of_week_label(self):
        coach = Coach.objects.get(id=1)
        field_label = coach._meta.get_field('days_of_week').verbose_name
        self.assertEqual(field_label, 'days_of_week')
    
    def test_coach_start_time_label(self):
        coach = Coach.objects.get(id=1)
        field_label = coach._meta.get_field('start_time').verbose_name
        self.assertEqual(field_label, 'start_time')
    
    def test_coach_end_time_label(self):
        coach = Coach.objects.get(id=1)
        field_label = coach._meta.get_field('end_time').verbose_name
        self.assertEqual(field_label, 'end_time')
    
    def test_coach_last_transaction_label(self):
        coach = Coach.objects.get(id=1)
        field_label = coach._meta.get_field('last_transaction').verbose_name
        self.assertEqual(field_label, 'last_payment_of_salary')
    
    def test_coach_transaction_amount_label(self):
        coach = Coach.objects.get(id=1)
        field_label = coach._meta.get_field('transaction_amount').verbose_name
        self.assertEqual(field_label, 'salary')

class FinancialTestCase(TestCase):
    @classmethod
    def setUp(cls):
        Person.objects.create(name='hamed', last_name='fathi', email='hamed.fathi@gmail.com',
        password='sthfortest')
        Income.objects.create(details='test1', date=now(), amount=10000,
        user=Person.objects.get(name='hamed'))
        Income.objects.create(details='test2', date=now(), amount=10000,
        user=Person.objects.get(name='hamed'))
        Expense.objects.create(details='test1', date=now(), amount=10000,
        user=Person.objects.get(name='hamed'))
        Expense.objects.create(details='test2', date=now(), amount=10000,
        user=Person.objects.get(name='hamed'))

    def test_transactions_display_name_in_admin_site(self):
        user = Person.objects.get(name='hamed')
        income = Income.objects.filter(user=user)[0]
        expense = Expense.objects.filter(user=user)[0]
        self.assertEqual(str(income), f'hamed_fathi {income.date} {income.amount} toman')
        self.assertEqual(str(expense), f'hamed_fathi {expense.date} {expense.amount} toman')

    def test_two_transaction_is_not_equal(self):
        user = Person.objects.get(name='hamed')
        income1, income2 = Income.objects.filter(user=user)
        expense1, expense2 = Expense.objects.filter(user=user)
        self.assertNotEqual(income1.code, income2.code)
        self.assertNotEqual(expense1.code, expense2.code)
