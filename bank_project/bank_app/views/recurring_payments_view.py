from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from datetime import datetime

from ..errors import InsufficientFunds, NotEverythingProvided
from ..forms import RecurringPaymentForm
from bank_app.models import Account, Recurring_Payment

@login_required
def recurring_payments(request):
    assert hasattr(
        request.user, 'customer'), 'Staff user routing customer view.'
    # maybe better have a function in customer
    recurring_payments = Recurring_Payment.get_recurring_payments_by_customer(
        request.user.customer)
    count_recurring_payments = len(recurring_payments)
    print("recurring_payments: ", recurring_payments)
    print("count_recurring_payments: ", count_recurring_payments)
    context = {
        'recurring_payments': recurring_payments,
        'count_recurring_payments': count_recurring_payments
    }
    return render(request, 'bank_app/recurring_payments.html', context)


@login_required
def add_recurring_payment(request):
    if request.method == 'POST':
        form = RecurringPaymentForm(request.POST)
        form.fields['sender_account'].queryset = request.user.customer.accounts
        if form.is_valid():
            sender_account = Account.objects.get(
                pk=form.cleaned_data['sender_account'].pk)
            receiver_account = Account.objects.get(
                pk=form.cleaned_data['receiver_account'])
            amount = form.cleaned_data['amount']
            text = form.cleaned_data['text']
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            pay_once_per_n_days = form.cleaned_data['pay_once_per_n_days']
            try:
                Recurring_Payment.add(request.user.customer, sender_account, receiver_account, text, amount,
                                      start_date, end_date, pay_once_per_n_days)
                # Recurring_Payment.pay_recurring_payments_for_today()
                return recurring_payments(request)
            except InsufficientFunds:
                context = {
                    'title': 'Payment error',
                    'error': 'Insufficient funds to set a recurring payment'
                }
                return render(request, 'bank_app/error.html', context)

    else:
        form = RecurringPaymentForm()
    print("request.user.customer.accounts: ", request.user.customer.accounts)
    form.fields['sender_account'].queryset = request.user.customer.accounts
    context = {
        'form': form,
    }
    return render(request, 'bank_app/add_recurring_payment.html', context)


@login_required
def update_recurring_payment(request, pk):
    recurring_payment = Recurring_Payment.objects.get(pk=pk)
    context = {
        'payment': recurring_payment
    }
    if request.method == 'POST':
        amount = request.POST['amount']
        text = request.POST['text']
        start_date = request.POST['start_date']
        end_date = request.POST['end_date']
        pay_once_per_n_days = request.POST['pay_once_per_n_days']
        try:
            if (not (amount and len(text) and len(str(start_date)) and len(str(end_date)) and pay_once_per_n_days)):
                print("amount", amount)
                print("text", text)
                print("start_date", start_date)
                print("end_date", end_date)
                print("pay_once_per_n_days", pay_once_per_n_days)
                recurring_payment = Recurring_Payment.objects.get(pk=pk)
                raise NotEverythingProvided('All fields have to be provided')

            if (datetime.strptime(start_date, '%Y-%m-%d') > datetime.strptime(end_date, '%Y-%m-%d')):
                raise NotEverythingProvided(
                    'Start Date can\'t be after End Date')

            recurring_payment.update_recurring_payment(
                text=text, amount=amount, start_date=start_date, end_date=end_date, pay_once_per_n_days=pay_once_per_n_days)
            # NOT SURE HOW IT WORKS IF account_details doesn't have pk field -- HAVE TO TEST
            return recurring_payments(request)
        except InsufficientFunds:
            context.update({
                'title': 'Payment error',
                'error': 'Insufficient funds to set a recurring payment'
            })

        except NotEverythingProvided as e:
            context.update({
                'title': 'Fields error',
                'error': f"{e}"
            })
            # return render(request, 'bank_app/error.html', context)

    return render(request, 'bank_app/update_recurring_payment.html', context)


@login_required
def delete_recurring_payment(request, pk):
    recurring_payment = Recurring_Payment.objects.get(pk=pk)
    recurring_payment.delete()
    return recurring_payments(request)