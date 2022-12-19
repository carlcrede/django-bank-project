from django.test import TestCase
from django.urls import reverse, resolve
from bank_app.views import index, customer_dashboard, employee_dashboard, account_details, make_transfer, get_loan, pay_loan, transaction_details, create_employee, create_customer, create_account, create_customer_account, rerank_customer, customer_details
from bank_app.models import Account, Customer, Employee, Ledger
from django.contrib.auth.models import User
from uuid import uuid4


# class TestUrls(TestCase):

#     def test_list_url_is_resolved(self):
#         url = reverse('bank_app:index')
#         self.assertEquals(resolve(url).func, index)

#     def test_customer_dashboard_url_is_resolved(self):
#         url = reverse('bank_app:customer_dashboard')
#         self.assertEquals(resolve(url).func, customer_dashboard)

#     def test_employee_dashboard_url_is_resolved(self):
#         url = reverse('bank_app:employee_dashboard')
#         self.assertEquals(resolve(url).func, employee_dashboard)

#     def test_account_details_url_is_resolved(self):
#         url = reverse('bank_app:account_details', args=['123456789'])
#         self.assertEquals(resolve(url).func, account_details)

#     def test_make_transfer_url_is_resolved(self):
#         url = reverse('bank_app:make_transfer')
#         self.assertEquals(resolve(url).func, make_transfer)

#     def test_get_loan_url_is_resolved(self):
#         url = reverse('bank_app:get_loan')
#         self.assertEquals(resolve(url).func, get_loan)

#     def test_pay_loan_url_is_resolved(self):
#         url = reverse('bank_app:pay_loan')
#         self.assertEquals(resolve(url).func, pay_loan)

    # def test_transaction_details_url_is_resolved(self):
    #     Ledger.objects.create(
    #         transaction_id=uuid4(),
    #         amount=100,
    #         text='test',
    #         account=Account.objects.create(
    #             name='testName',
    #             is_loan=False,
    #             ban='123456789',
    #             iban='123456789',
    #             customer=Customer.objects.create(
    #                 user=User.objects.create_user(
    #                     username='testUser',
    #                     password='testPassword',
    #                     email='testEmail'
    #                 )
    #             ),
    #             created_at='2020-01-01 00:00:00',
    #             deactivated=False
    #         )
    #     )
    #     url = reverse('bank_app:transaction_details', args=[
    #                   Ledger.objects.first().transaction_id])
    #     self.assertEquals(resolve(url).func, transaction_details)

    # def test_create_employee_url_is_resolved(self):
    #     url = reverse('bank_app:create_employee')
    #     self.assertEquals(resolve(url).func, create_employee)

    # def test_create_customer_url_is_resolved(self):
    #     url = reverse('bank_app:create_customer')
    #     self.assertEquals(resolve(url).func, create_customer)

    # def test_create_account_url_is_resolved(self):
    #     url = reverse('bank_app:create_account')
    #     self.assertEquals(resolve(url).func, create_account)

    # def test_create_customer_account_url_is_resolved(self):
    #     url = reverse('bank_app:create_customer_account', args=['123456789'])
    #     self.assertEquals(resolve(url).func, create_customer_account)

    # def test_rerank_customer_url_is_resolved(self):
    #     url = reverse('bank_app:rerank_customer', args=['123456789'])
    #     self.assertEquals(resolve(url).func, rerank_customer)

    # def test_customer_details_url_is_resolved(self):
    #     url = reverse('bank_app:customer_details', args=['123456789'])
    #     self.assertEquals(resolve(url).func, customer_details)
