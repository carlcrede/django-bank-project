import httpx
import django_rq

from rq import Retry
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db import transaction

from .shared_view import account_details
from ..errors import InsufficientFunds
from ..forms import ExternalTransferForm, TransferForm
from bank_app.models import Account, Ledger, Customer, ExternalTransfer
from bank_app.models.external_transfer import transfer_failed
from ..serializers import ExternalTransferSerializer

@login_required
def make_transfer(request):
    assert hasattr(
        request.user, 'customer'), 'Staff user routing customer view.'

    if request.method == 'POST':
        form = TransferForm(request.POST)
        form.fields['debit_account'].queryset = request.user.customer.accounts
        if form.is_valid():
            amount = form.cleaned_data['amount']
            debit_account = Account.objects.get(
                pk=form.cleaned_data['debit_account'].pk)
            debit_text = form.cleaned_data['debit_text']
            credit_account = Account.objects.get(
                pk=form.cleaned_data['credit_account'])
            credit_text = form.cleaned_data['credit_text']
            try:
                transfer = Ledger.transfer(
                    amount, debit_account, debit_text, credit_account, credit_text)
                # NOT SURE HOW IT WORKS IF account_details doesn't have pk field -- HAVE TO TEST
                return account_details(request, ban=debit_account.pk)
            except InsufficientFunds:
                context = {
                    'title': 'Transfer error',
                    'error': 'Insufficient funds for transfer'
                }
                return render(request, 'bank_app/error.html', context)

    else:
        form = TransferForm()

    form.fields['debit_account'].queryset = request.user.customer.accounts
    context = {
        'form': form
    }
    return render(request, 'bank_app/make_transfer.html', context)



@login_required
def make_external_transfer(request):
    assert hasattr(
        
        request.user, 'customer'), 'Staff user routing customer view.'

    if request.method == 'POST':
        form = ExternalTransferForm(request.POST)
        form.fields['debit_account'].queryset = request.user.customer.accounts
        if form.is_valid():
            amount = form.cleaned_data['amount']
            debit_account = Account.objects.get(
                pk=form.cleaned_data['debit_account'].pk)
            debit_text = form.cleaned_data['debit_text']
            credit_account = form.cleaned_data['credit_account']
            credit_text = form.cleaned_data['credit_text']
            to_bank = form.cleaned_data['to_bank']
            bank_url = form.cleaned_data['bank_url']
            print(bank_url)
            try:
                with transaction.atomic():
                    t = ExternalTransfer.create(
                        amount=amount,
                        debit_account=debit_account,
                        credit_account=credit_account,
                        to_bank=to_bank,
                        text=credit_text
                    )
                data = ExternalTransferSerializer(t)
                ext_t_acc = Customer.external_transactions_acc()
                django_rq.enqueue(
                    ExternalTransfer.reserve_transfer, data, t, ext_t_acc, debit_account, bank_url,
                    retry=Retry(max=3, interval=5),
                    on_failure=transfer_failed,
                )
                return external_transfers_overview(request)
            except httpx.HTTPStatusError as err:
                print(err)
            except InsufficientFunds:
                context = {
                    'title': 'Transfer error',
                    'error': 'Insufficient funds for transfer'
                }
                return render(request, 'bank_app/error.html', context)
            except Exception as e:
                context = {
                    'title': 'Internal server error',
                    'error': e.message
                }
                return render(request, 'bank_app/error.html', context)
    else:
        form = ExternalTransferForm()

    form.fields['debit_account'].queryset = request.user.customer.accounts
    context = {
        'form': form
    }
    return render(request, 'bank_app/make_external_transfer.html', context)

@login_required
def external_transfers_overview(request):
    external_transfers = request.user.customer.external_transfers_sent.order_by('-created_at')[:10]
    context = {
        'external_transfers': external_transfers
    }
    return render(request, 'bank_app/external_transfers_overview.html', context)