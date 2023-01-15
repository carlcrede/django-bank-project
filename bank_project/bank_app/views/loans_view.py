
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from .shared_view import account_details

from ..errors import InsufficientFunds
from ..forms import PayLoanForm
from bank_app.models import Customer

@login_required
def loans(request):
    print("In the loans view")
    assert hasattr(request.user, 'customer'), 'Staff user routing customer view.'

    customer_loans = request.user.customer.loans
    context = {'loans': customer_loans }
    return render(request, 'bank_app/loans.html', context)


@login_required
def get_loan(request):
    context = {}
    assert hasattr(
        request.user, 'customer'), 'Staff user routing customer view.'
    assert (request.user.customer.rank !=
            'BASIC'), 'Customer with BASIC rank cannnot make/pay a loan'
    if request.method == 'POST':
        print("request.POST: ", request.POST)
        print("request.user: ", request.user.customer)
        amount = request.POST['amount']
        if float(amount) < 0:
            context = {
                'title': 'Get Loan error',
                'error': '!!!!Amount must be positive!!!!'
            }
            return render(request, 'bank_app/get_loan.html', context)

        ban = request.POST['ban']
        print("get_loan: ", amount, ban)
        customer = Customer.objects.get(user=request.user)
        loan = customer.get_loan(ban, amount)
        print("Customer accounts: ", customer.accounts)
        print("Customer loans: ", customer.loans)
        print("loan: ", loan)
        # form = TransferForm(request.POST)
        # form.fields['debit_account'].queryset = request.user.customer.accounts
        # if form.is_valid():
        #     amount = form.cleaned_data['amount']
        #     debit_account = Account.objects.get(pk=form.cleaned_data['debit_account'].pk)
        #     debit_text = form.cleaned_data['debit_text']
        #     credit_account = Account.objects.get(pk=form.cleaned_data['credit_account'])
        #     credit_text = form.cleaned_data['credit_text']
        #     try:
        #         transfer = Ledger.transfer(amount, debit_account, debit_text, credit_account, credit_text)
        #         return account_details(request, pk=debit_account.pk)
        #     except InsufficientFunds:
        #         context = {
        #             'title': 'Transfer error',
        #             'error': 'Insufficient funds for transfer'
        #         }
        #         return render(request, 'bank_app/error.html', context)
        # return HttpResponseRedirect(reverse('bank_app:customer_dashboard'))

        return account_details(request, ban=loan.pk)
    return render(request, 'bank_app/get_loan.html', context)


@login_required
def pay_loan(request):
    assert hasattr(
        request.user, 'customer'), 'Staff user routing customer view.'
    assert (request.user.customer.rank !=
            'BASIC'), 'Customer with BASIC rank cannnot make/pay a loan'
    if request.method == 'POST':
        form = PayLoanForm(request.POST)
        form.fields['customer_account'].queryset = request.user.customer.accounts
        form.fields['loan_account'].queryset = request.user.customer.loans
        if form.is_valid():
            customer = Customer.objects.get(user=request.user)
            amount = form.cleaned_data['amount']
            see_loan_account = form.cleaned_data['loan_account']
            print("see_loan_account: ", see_loan_account)
            customer_account = form.cleaned_data['customer_account']
            customer_text = form.cleaned_data['customer_text']
            print("loan_account type: ", type(
                form.cleaned_data['loan_account'].pk))
            loan_account = form.cleaned_data['loan_account']
            loan_text = form.cleaned_data['loan_text']
            print(f"amount: {amount}, customer_account: {customer_account}, customer_text: {customer_text}, loan_account: {loan_account}, loan_text:{loan_text}")
            try:
                customer_account = customer.pay_loan(
                    amount, customer_account, customer_text, loan_account, loan_text)
                return account_details(request, ban=customer_account.pk)
            except InsufficientFunds:
                context = {
                    'title': 'Pay Loan error',
                    'error': 'Insufficient funds to pay the loan'
                }
                return render(request, 'bank_app/error.html', context)

    else:
        form = PayLoanForm()

    form.fields['customer_account'].queryset = request.user.customer.accounts
    form.fields['loan_account'].queryset = request.user.customer.loans
    context = {
        'form': form
    }
    return render(request, 'bank_app/pay_loan.html', context)