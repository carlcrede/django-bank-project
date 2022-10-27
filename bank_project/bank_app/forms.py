from django import forms
from django.core.exceptions import ObjectDoesNotExist
from .models import Customer, Account


class TransferForm(forms.Form):
    amount = forms.DecimalField(label='Amount', max_digits=10)
    debit_account = forms.ModelChoiceField(label='Debit Account', queryset=Customer.objects.none())
    debit_text = forms.CharField(label='Debit Text', max_length=200)
    credit_account = forms.CharField(label='Credit Account number')
    credit_text = forms.CharField(label='Credit Text', max_length=200)

    # TODO: probably need another way to identify the credit account, since they atm just use the pk,
    # and the UUID is kinda too long and complicated to be used by customers easily. Should maybe be a IBAN or
    # closer to the account ID's we know from our own accounts

    def clean(self):
        super().clean()

        credit_account = self.cleaned_data.get('credit_account')
        try:
            print("credit_account:", credit_account)
            print(type(credit_account))
            Account.objects.get(pk=credit_account)
        except ObjectDoesNotExist:
            self._errors['credit_account'] = self.error_class(['Credit account not found.'])

        if self.cleaned_data.get('amount') < 0:
            self._errors['amount'] = self.error_class(['Amount must be positive.'])

        return self.cleaned_data

class PayLoanForm(forms.Form):
    amount = forms.DecimalField(label='Amount', max_digits=10)
    customer_account = forms.ModelChoiceField(label='Debit Account', queryset=Customer.objects.none())
    customer_text = forms.CharField(label='Debit Text', max_length=200)
    loan_account = forms.ModelChoiceField(label='Loan Account', queryset=Customer.objects.none())
    loan_text = forms.CharField(label='Loan Text', max_length=200)

    def clean(self):
        loan_account = self.cleaned_data.get('loan_account')
        loan_account_balance = loan_account.balance
        customer_account = self.cleaned_data.get('customer_account')
        customer_account_balance = customer_account.balance

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