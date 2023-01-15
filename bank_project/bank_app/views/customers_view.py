from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from bank_app.models import Ledger

@login_required
def customer_dashboard(request):
    assert hasattr(
        request.user, 'customer'), 'Staff user routing customer view.'

    accounts = request.user.customer.accounts
    loans = request.user.customer.loans
    context = {
        'accounts': accounts,
        'loans': loans
    }
    return render(request, 'bank_app/customer_dashboard.html', context)

@login_required
def transaction_details(request, transaction_id):
    t = Ledger.objects.filter(transaction_id=transaction_id)
    credit = t[0] if t[0].amount > 0 else t[1]
    debit = t[0] if t[0].amount <= 0 else t[1]
    context = {
        'credit': credit,
        'debit': debit,
        'transaction_id': transaction_id
    }
    return render(request, 'bank_app/transaction_details.html', context)