from django.test import TestCase
from users.models import *
# Create your tests here.
class PersonTestCase(TestCase):
    @classmethod
    def setUp(cls):
        Person.objects.create(name='hamed', last_name='fathi', email='hamed.fathi@gmail.com',
        password='sthfortest')
        Person.objects.create(name='hamid', last_name='fathi', email='hamid.fathi@gmail.com',
        password='sthelsefortest')
        Token.objects.create(token='sth', user=Person.objects.get(name='hamed'))
        Coach.objects.create(age=20, sport_field='F', days_of_week=['1', '2'],
        user=Person.objects.get(name='hamed'), salary=20000)
        Athlete.objects.create(age=20, sport_field='F', days_of_week=['1', '2'],
        user=Person.objects.get(name='hamid'), trainer=Person.objects.get(name='hamed'))

    def test_person_display_name_in_admin_site(self):
        user = Person.objects.get(name='hamed')
        token = Token.objects.get(user=user)
        coach = Person.objects.get(name='hamed')
        athlete = Person.objects.get(name='hamid')
        self.assertEqual(str(user), 'hamed_fathi')
        self.assertEqual(str(token), 'hamed.fathi@gmail.com_token')
        self.assertEqual(str(coach), 'hamed_fathi')
        self.assertEqual(str(athlete), 'hamid_fathi')

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
