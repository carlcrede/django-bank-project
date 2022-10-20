from django import forms
from django.core.exceptions import ObjectDoesNotExist
from .models import Customer, Account


class TransferForm(forms.Form):
    amount = forms.DecimalField(label='Amount', max_digits=10)
    debit_account = forms.ModelChoiceField(label='Debit Account', queryset=Customer.objects.none())
    debit_text = forms.CharField(label='Debit Text', max_length=200)
    credit_account = forms.IntegerField(label='Credit Account number')
    credit_text = forms.CharField(label='Credit Text', max_length=200)

    # TODO: probably need another way to identify the credit account, since they atm just use the pk,
    # and the UUID is kinda too long and complicated to be used by customers easily. Should maybe be a IBAN or
    # closer to the account ID's we know from our own accounts

    def clean(self):
        super().clean()

        credit_account = self.cleaned_data.get('credit_account')
        try:
            Account.objects.get(pk=credit_account)
        except ObjectDoesNotExist:
            self._errors['credit_account'] = self.error_class(['Credit account not found.'])

        if self.cleaned_data.get('amount') < 0:
            self._errors['amount'] = self.error_class(['Amount must be positive.'])

        return self.cleaned_data

class PayLoanForm(forms.Form):
    amount = forms.DecimalField(label='Amount', max_digits=10)
    debit_account = forms.ModelChoiceField(label='Debit Account', queryset=Customer.objects.none())
    debit_text = forms.CharField(label='Debit Text', max_length=200)
    credit_account = forms.ModelChoiceField(label='Loan Account', queryset=Customer.objects.none())
    credit_text = forms.CharField(label='Credit Text', max_length=200)

    def clean(self):
        super().clean()
        if self.cleaned_data.get('amount') < 0:
            self._errors['amount'] = self.error_class(['Amount must be positive.'])

        return self.cleaned_data