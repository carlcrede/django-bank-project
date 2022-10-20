from django.shortcuts import HttpResponse, get_object_or_404, render, reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required

from .errors import InsufficientFunds

from .forms import TransferForm, PayLoanForm
from .models import Employee, Account, Ledger, Customer

@login_required
def index(request):
    if hasattr(request.user, 'employee'):
        print("employee")
        # return HttpResponseRedirect(reverse('bank:staff_dashboard'))
        return HttpResponseRedirect(reverse('bank_app:employee_dashboard'))
    elif hasattr(request.user, 'customer'):
        return HttpResponseRedirect(reverse('bank_app:customer_dashboard'))

    return render(request, 'bank_app/error.html', {'error': 'Fatal error. Should never happen'})

@login_required
def customer_dashboard(request):
    assert hasattr(request.user, 'customer'), 'Staff user routing customer view.'

    accounts = request.user.customer.accounts
    loans = request.user.customer.loans
    context = {
        'accounts': accounts,
        'loans': loans
    }
    return render(request, 'bank_app/customer_dashboard.html', context)
    
@login_required
def employee_dashboard(request):
    assert hasattr(request.user, 'employee'), 'Staff user routing customer view.'

    customers = Customer.objects.all()
    context = {
        'customers': customers,
    }
    return render(request, 'bank_app/employee_dashboard.html', context)


@login_required
def account_details(request, ban):
    if hasattr(request.user, 'customer'):
        'Staff user routing customer view.'
        account = get_object_or_404(Account, customer=request.user.customer, pk=ban)
        context = {
            'is_employee': False,
            'account': account
        }
        return render(request, 'bank_app/account_details.html', context)
    elif hasattr(request.user, 'employee'):
        account = get_object_or_404(Account, pk=ban)
        context = {
            'is_employee': True,
            'account': account
        }
        return render(request, 'bank_app/account_details.html', context)

@login_required
def transaction_details(request, transaction_id):
    t = Ledger.objects.filter(transaction_id=transaction_id)
    credit = t[0] if t[0].amount > 0 else t[1]
    debit =  t[0] if t[0].amount <= 0 else t[1]
    context = {
        'credit': credit,
        'debit': debit,
        'transaction_id': transaction_id
    }
    return render(request, 'bank_app/transaction_details.html', context)

@login_required
def make_transfer(request):
    assert hasattr(request.user, 'customer'), 'Staff user routing customer view.'

    if request.method == 'POST':
        form = TransferForm(request.POST)
        form.fields['debit_account'].queryset = request.user.customer.accounts
        if form.is_valid():
            amount = form.cleaned_data['amount']
            debit_account = Account.objects.get(pk=form.cleaned_data['debit_account'].pk)
            debit_text = form.cleaned_data['debit_text']
            credit_account = Account.objects.get(pk=form.cleaned_data['credit_account'])
            credit_text = form.cleaned_data['credit_text']
            try:
                transfer = Ledger.transfer(amount, debit_account, debit_text, credit_account, credit_text)
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
def get_loan(request):
    context = {}
    assert hasattr(request.user, 'customer'), 'Staff user routing customer view.'
    assert ( request.user.customer.rank == 'BASIC'), 'Customer with BASIC rank cannnot make a loan'
    if request.method == 'POST':
        print("request.POST: ", request.POST)
        print("request.user: ", request.user.customer)
        amount = request.POST['amount']
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
    assert hasattr(request.user, 'customer'), 'Staff user routing customer view.'

    if request.method == 'POST':
        form = PayLoanForm(request.POST)
        form.fields['debit_account'].queryset = request.user.customer.accounts
        form.fields['credit_account'].queryset = request.user.customer.loans
        if form.is_valid():
            amount = form.cleaned_data['amount']
            debit_account = Account.objects.get(pk=form.cleaned_data['debit_account'].pk)
            debit_text = form.cleaned_data['debit_text']
            credit_account = Account.objects.get(pk=form.cleaned_data['credit_account'].pk)
            credit_text = form.cleaned_data['credit_text']
            try:
                transfer = Ledger.transfer(amount, debit_account, debit_text, credit_account, credit_text)
                return account_details(request, ban=debit_account.pk)
            except InsufficientFunds:
                context = {
                    'title': 'Transfer error',
                    'error': 'Insufficient funds for transfer'
                }
                return render(request, 'bank_app/error.html', context)

    else:
        form = PayLoanForm()
    
    form.fields['debit_account'].queryset = request.user.customer.accounts
    form.fields['credit_account'].queryset = request.user.customer.loans
    context = {
        'form': form
    }
    return render(request, 'bank_app/pay_loan.html', context)


def create_employee(request):
    context = {}
    if request.method == "POST":
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        user_name = request.POST['user_name']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        if password == confirm_password:
            Employee.create_employee(first_name, last_name, email, user_name, password)
            # if :
            return HttpResponseRedirect(reverse('bank_app:index'))
            # else:
            #    context = {
            #       'error': 'Could not create user account - please try again.'
            #    }
        else:
            context = {
                'error': 'Passwords did not match. Please try again.'
            }
    return render(request, 'bank_app/create_employee.html', context)

def create_customer(request):
    context = {}
    if request.method == "POST":
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        user_name = request.POST['user_name']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        phone = request.POST['phone']
        rank = request.POST['rank']
        if password == confirm_password:
            Employee.create_customer(first_name, last_name, email, user_name, phone, rank, password)
            # if :
            return HttpResponseRedirect(reverse('bank_app:index'))
            # else:
            #    context = {
            #       'error': 'Could not create user account - please try again.'
            #    }
        else:
            context = {
                'error': 'Passwords did not match. Please try again.'
            }
    return render(request, 'bank_app/create_customer.html', context)

def create_account(request):
    context = {}
    if request.method == "POST":
        customer_username = request.POST['customer']
        account_name = request.POST['name']
        Employee.create_account(customer_username, account_name)
        return HttpResponseRedirect(reverse('bank_app:index'))
    return render(request, 'bank_app/create_account.html', context)

def create_customer_account(request, customer_username):
    context = {'customer_username': customer_username}
    if request.method == "POST":
        account_name = request.POST['name']
        Employee.create_account(customer_username, account_name)
        return HttpResponseRedirect(reverse('bank_app:employee_dashboard'))
    return render(request, 'bank_app/create_customer_account.html', context)

def rerank_customer(request, customer_username):
    context = {'customer_username': customer_username}
    if request.method == "POST":
        rank = request.POST['rank']
        Employee.rerank_customer(customer_username, rank)
        return HttpResponseRedirect(reverse('bank_app:employee_dashboard'))
    return render(request, 'bank_app/rerank_customer.html', context)

def customer_details(request, customer_username):
    customer = get_object_or_404(Customer, user__username=customer_username)
    accounts = customer.accounts
    context = {
        'customer': customer,
        'accounts': accounts,
    }
    return render(request, 'bank_app/customer_details.html', context)