from django.test import TestCase, Client
from django.urls import reverse
from bank_app.models import Account, Customer, Employee, Ledger
from django.contrib.auth.models import User
from unittest import mock

import json

mockEmployee = mock.Mock(spec=Employee)

class TestViews(TestCase):

    def setUp(self):
        self.client = Client()
        self.index_url = reverse('bank_app:index')
        self.customer_dashboard_url = reverse('bank_app:customer_dashboard')
        self.employee_dashboard_url = reverse('bank_app:employee_dashboard')
        self.make_transfer_url = reverse('bank_app:make_transfer')
        self.create_employee_url = reverse('bank_app:create_employee')
        self.uuid = '123e4567-e89b-12d3-a456-426655440000'
        self.account_details_url = reverse(
            'bank_app:account_details', args=['123456789'])
        self.transaction_details_url = reverse(
            'bank_app:transaction_details', args=[self.uuid])
        self.customer = Customer.objects.create(
            user=User.objects.create_user(
                username='customerUsername',
                password='customerPassword',
                email='customerEmail'
            )
        )
        self.employee = Employee.objects.create(
            user=User.objects.create_user(
                username='employeeUsername',
                password='employeePassword',
                email='employeeEmail'
            )
        )
        # self.bank_account = Account.objects.create(
        #     name='bankAccount',
        #     is_loan=False,
        #     ban='000000000',
        #     iban='00000000000000000000000000',
        #     customer=self.customer,
        #     created_at='2020-01-01 00:00:00',
        #     deactivated=False
        # )
        self.customer_account_1 = Account.objects.create(
            name='customerAccount1',
            is_loan=False,
            ban='123456789',
            iban='123456789',
            customer=self.customer,
            created_at='2020-01-01 00:00:00',
            deactivated=False
        )
        self.customer_account_2 = Account.objects.create(
            name='customerAccount2',
            is_loan=False,
            ban='987654321',
            iban='987654321',
            customer=self.customer,
            created_at='2020-01-01 00:00:00',
            deactivated=False
        )
        self.ledger1 = Ledger.objects.create(
            transaction_id=self.uuid,
            amount=100,
            text='transactionText',
            account=self.customer_account_1,
            created_at='2020-01-01 00:00:00',
            direct_transaction_with_bank=False
        )
        self.ledger2 = Ledger.objects.create(
            transaction_id=self.uuid,
            amount=-100,
            text='transactionText',
            account=self.customer_account_2,
            created_at='2020-01-01 00:00:00',
            direct_transaction_with_bank=False
        )

    def test_index_customer_GET(self):
        self.client.login(username='customerUsername',
                          password='customerPassword')
        response = self.client.get(self.index_url, follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'bank_app/customer_dashboard.html')

    def test_index_employee_GET(self):
        self.client.login(username='employeeUsername',
                          password='employeePassword')
        response = self.client.get(self.index_url, follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'bank_app/employee_dashboard.html')

    def test_dashboard_GET_customer(self):
        self.client.login(username='customerUsername',
                          password='customerPassword')
        response = self.client.get(self.customer_dashboard_url, follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'bank_app/customer_dashboard.html')

    def test_dashboard_GET_employee(self):
        self.client.login(username='employeeUsername',
                          password='employeePassword')
        response = self.client.get(self.employee_dashboard_url, follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'bank_app/employee_dashboard.html')

    def test_account_details_GET_customer(self):
        self.client.login(username='customerUsername',
                          password='customerPassword')
        response = self.client.get(self.account_details_url, follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'bank_app/account_details.html')

    def test_account_details_GET_employee(self):
        self.client.login(username='employeeUsername',
                          password='employeePassword')
        response = self.client.get(self.account_details_url, follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'bank_app/account_details.html')

    def test_transaction_details_GET(self):
        self.client.login(username='customerUsername',
                          password='customerPassword')
        response = self.client.get(self.transaction_details_url, follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'bank_app/transaction_details.html')

    # def test_make_transfer_POST(self):
    #     self.client.login(username='customerUsername',
    #                       password='customerPassword')
    #     response = self.client.post(
    #         self.make_transfer_url,
    #         {
    #             'amount': 1000,
    #             'text': 'transactionText',
    #             'account': self.customer_account_1.ban,
    #             'recipient': self.customer_account_2.ban
    #         },
    #         follow=True
    #     )
    #     self.assertEquals(response.status_code, 200)
    #     self.assertTemplateUsed(response, 'bank_app/make_transfer.html')

    def test_create_employee_POST(self):
        self.client.login(username='employeeUsername',
                          password='employeePassword')
        response = self.client.post(
            self.create_employee_url,
            {
                'user_name': 'newEmployeeUsername',
                'password': 'newEmployeePassword',
                'confirm_password': 'newEmployeePassword',
                'email': 'newEmployeeEmail',
                'first_name': 'newEmployeeFirstName',
                'last_name': 'newEmployeeLastName'
            },
            follow=True
        )
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'bank_app/employee_dashboard.html')
        mockEmployee.create_employee.assert_called_once_with(
            'newEmployeeFirstName',
            'newEmployeeLastName',
            'newEmployeeEmail',
            'newEmployeeUsername',
            'newEmployeePassword'
        )

    def test_create_employee_POST_wrong_confirm_password(self):
        self.client.login(username='employeeUsername',
                          password='employeePassword')
        response = self.client.post(
            self.create_employee_url,
            {
                'user_name': 'newEmployeeUsername',
                'password': 'newEmployeePassword',
                'confirm_password': 'newEmployeePassword2',
                'email': 'newEmployeeEmail',
                'first_name': 'newEmployeeFirstName',
                'last_name': 'newEmployeeLastName'
            },
            follow=True
        )
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'bank_app/create_employee.html')
        self.assertEquals(
            response.context['error'], 'Passwords did not match. Please try again.')
