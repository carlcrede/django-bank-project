from django import forms
from django.core.exceptions import ObjectDoesNotExist
from .models import Customer, Account, Stock
from datetime import datetime
from .util import get_external_bank_url
from django.conf import settings

class TransferForm(forms.Form):
    amount = forms.DecimalField(label='Amount', max_digits=10)
    debit_account = forms.ModelChoiceField(label='Debit Account', queryset=Customer.objects.none())
    debit_text = forms.CharField(label='Debit Text', max_length=200)
    credit_account = forms.CharField(label='Credit Account number')
    credit_text = forms.CharField(label='Credit Text', max_length=200)

    def clean(self):
        super().clean()

        credit_account = self.cleaned_data.get('credit_account')
        try:
            Account.objects.get(pk=credit_account)
        except ObjectDoesNotExist:
            self._errors['credit_account'] = self.error_class(['Credit account not found.'])

        if self.cleaned_data.get('amount') <= 0:
            self._errors['amount'] = self.error_class(['Amount must be positive.'])

        return self.cleaned_data

class ExternalTransferForm(TransferForm):
    to_bank = forms.CharField(label='Bank registration number', max_length=4)
    def clean(self):
        if self.cleaned_data.get('amount') <= 0:
            self._errors['amount'] = self.error_class(['Amount must be positive.'])

        registration_number = self.cleaned_data.get('to_bank')

        if registration_number == settings.BANK_REGISTRATION_NUMBER:
            self._errors['to_bank'] = self.error_class(['You must enter the registration number of another bank'])

        bank_url = get_external_bank_url(registration_number=registration_number)
        if not bank_url:
            self._errors['to_bank'] = self.error_class(['Invalid bank registration number'])

        self.cleaned_data['bank_url'] = bank_url

        return self.cleaned_data

class PayLoanForm(forms.Form):
    amount = forms.DecimalField(label='Amount', max_digits=10)
    customer_account = forms.ModelChoiceField(label='Debit Account', queryset=Account.objects.none())
    customer_text = forms.CharField(label='Debit Text', max_length=200)
    loan_account = forms.ModelChoiceField(label='Loan Account', queryset=Account.objects.none())
    loan_text = forms.CharField(label='Loan Text', max_length=200)

    def clean(self):
        loan_account = self.cleaned_data.get('loan_account')
        loan_account_balance = loan_account.available_balance
        customer_account = self.cleaned_data.get('customer_account')
        customer_account_balance = customer_account.available_balance

        super().clean()
        if self.cleaned_data.get('amount') < 0:
            self._errors['amount'] = self.error_class(['Amount must be positive.'])
        
        try:
            Account.objects.get(pk=customer_account.pk)
        except ObjectDoesNotExist:
            self._errors['customer_account'] = self.error_class(['Debit account not found.'])
        
        try:
            Account.objects.get(pk=loan_account.pk)
        except ObjectDoesNotExist:
            self._errors['loan_account'] = self.error_class(['Loan account not found.'])
        
        print("loan balance:", loan_account_balance)
        if self.cleaned_data.get('amount') > abs(loan_account_balance):
            self._errors['amount'] = self.error_class([f'Amount should be less or equal to loan amount. Loan amount for specified loan is: {loan_account_balance}'])
        
        if self.cleaned_data.get('amount') > customer_account_balance:
            self._errors['amount'] = self.error_class([f'Insufficient funds to pay the loan with specified amount'])
        
        return self.cleaned_data

class RecurringPaymentForm(forms.Form):
    sender_account = forms.ModelChoiceField(label='Your Account', queryset=Account.objects.none())
    receiver_account = forms.CharField(label='Reciever\'s Account number')
    amount = forms.DecimalField(label='Amount', max_digits=10)
    text = forms.CharField(label='Message', max_length=200)
    start_date = forms.DateField(widget=forms.DateInput(attrs=dict(type='date', min=datetime.now().date)), label="Start Date")
    end_date = forms.DateField(widget=forms.DateInput(attrs=dict(type='date', min=datetime.now().date)), label="End Date")
    pay_once_per_n_days = forms.IntegerField(label="Frequency of payments. Pay once every ??? days.", min_value=1, max_value=365)

    # TODO: probably need another way to identify the credit account, since they atm just use the pk,
    # and the UUID is kinda too long and complicated to be used by customers easily. Should maybe be a IBAN or
    # closer to the account ID's we know from our own accounts

    def clean(self):
        super().clean()
        customer_account = self.cleaned_data.get('sender_account')
        print("customer_account: ", customer_account)
        customer_account_balance = customer_account.available_balance
        
        # credit_account = self.cleaned_data.get('credit_account')
        # try:
        #     print("credit_account:", credit_account)
        #     print(type(credit_account))
        #     Account.objects.get(pk=credit_account)
        # except ObjectDoesNotExist:
        #     self._errors['credit_account'] = self.error_class(['Credit account not found.'])

        if self.cleaned_data.get('amount') < 0:
            self._errors['amount'] = self.error_class(['Amount must be positive.'])

        if self.cleaned_data.get('amount') > customer_account_balance:
            self._errors['amount'] = self.error_class(['Insufficient funds to make the recurring payment with specified amount'])
       
        if self.cleaned_data.get('start_date') > self.cleaned_data.get('end_date'):
            self._errors['start_date'] = self.error_class(['Start Date can\'t be after End Date'])

        return self.cleaned_data
        
    
class StockForm(forms.Form):
    stock = forms.ModelChoiceField(label='Choose Stock', queryset=Stock.objects.none())
    stock_volume = forms.IntegerField(label='Stock Amount')
    customer_account = forms.ModelChoiceField(label='Account used for payment', queryset=Account.objects.none())

    def clean(self):
        super().clean()

        if self.cleaned_data.get('stock_volume') < 0:
            self._errors['stock_volume'] = self.error_class(['Stock volume must be positive.'])
        
        stock_volume_of_the_chosen_stock = self.cleaned_data.get('stock').stock_volume
        if stock_volume_of_the_chosen_stock < self.cleaned_data.get('stock_volume'):
            self._errors['stock_volume'] = self.error_class([f'Chosen stock volume is bigger then what is available. Currently the stock volume is: {stock_volume_of_the_chosen_stock}'])

        
        # credit_account = self.cleaned_data.get('credit_account')
        # try:
        #     Account.objects.get(pk=credit_account)
        # except ObjectDoesNotExist:
        #     self._errors['credit_account'] = self.error_class(['Credit account not found.'])

        # if self.buyer_account.get('amount') <= 0:
        #     self._errors['amount'] = self.error_class(['Amount must be positive.'])

        return self.cleaned_data
