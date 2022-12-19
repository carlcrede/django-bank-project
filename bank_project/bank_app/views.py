from django.shortcuts import HttpResponse, get_object_or_404, render, reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
import pyotp
import os
import base64
from PIL import Image
import subprocess
from django.core.mail import send_mail
from django.core import mail

# This is our shell command, executed by Popen.



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
    assert ( request.user.customer.rank != 'BASIC'), 'Customer with BASIC rank cannnot make/pay a loan'
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
    assert hasattr(request.user, 'customer'), 'Staff user routing customer view.'
    assert ( request.user.customer.rank != 'BASIC'), 'Customer with BASIC rank cannnot make/pay a loan'
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
            print("loan_account type: ", type(form.cleaned_data['loan_account'].pk))
            loan_account = form.cleaned_data['loan_account']
            loan_text = form.cleaned_data['loan_text']
            print(f"amount: {amount}, customer_account: {customer_account}, customer_text: {customer_text}, loan_account: {loan_account}, loan_text:{loan_text}")
            try:
                customer_account = customer.pay_loan(amount, customer_account, customer_text, loan_account, loan_text)
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

@login_required
def enable_2fa(request):
    print("In the enable_2fa view")
    assert hasattr(request.user, 'customer'), 'Staff user routing customer view.'
    customer = Customer.objects.get(user=request.user)
    customer_has_enabled_2fa = (len(str(customer.secret_for_2fa)) != 0)
    print(customer_has_enabled_2fa)
    context = {'customer': customer, 'enabled_2fa': customer_has_enabled_2fa}
    return render(request, 'bank_app/enable_2fa.html', context)

@login_required
def enable_email_auth(request):
    print("In the enable_email_auth view")
    assert hasattr(request.user, 'employee'), 'Customer user routing customer view.'
    employee = Employee.objects.get(user=request.user)
    employee_email = employee.user.email
    employee_has_enabled_email_auth = (employee.secret_for_email_auth is not None)
    print(employee_has_enabled_email_auth)
    context = {'employee_email': employee_email, 'enabled_email_auth': employee_has_enabled_email_auth}
    return render(request, 'bank_app/enable_email_auth.html', context)

@login_required
def generate_2fa(request):
    print("In the enable_2fa view")
    assert hasattr(request.user, 'customer'), 'Staff user routing customer view.'
    customer = Customer.objects.get(user=request.user)
    context = {'customer': customer}
    
    print("In the enable_2fa view > POST")
    secret_for_2fa = pyotp.random_base32()
    string_for_2fa = f"otpauth://totp/Bank%20Project:%20{customer.user.first_name}%20{customer.user.last_name}?secret={secret_for_2fa}&issuer=Bank%20Project"
    qr_file_path=f"./bank_app/qrcodes/{customer.user.first_name}-{customer.user.last_name}.txt"
    type = "UTF8"
    generate_qrcode = f"qrencode -o {qr_file_path} {string_for_2fa}"
    print(generate_qrcode)

#         <img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAHElEQVQI12P4
#   //8/w38GIAXDIBKE0DHxgljNBAAO9TXL0Y4OHwAAAABJRU5ErkJggg==" alt="Red dot" />
    print("generate_qrcode here")
    p = subprocess.Popen(generate_qrcode, stdout=subprocess.PIPE, shell=True)

    # print(p.stdout.read())
    print(p.communicate())
    # print("gen, ", gen)
    print("generate_qrcode there")
    # while not os.path.exists(qr_file_path):
    #     print("in while loop")
    #     print(os.path.exists(qr_file_path))
    if (os.path.exists(qr_file_path)): 
        # os.system("ls  -R")   
        with open(qr_file_path, "r+b") as f:
            file = f.read()
            encoded_qrcode = base64.b64encode(file).decode("utf-8")
            print(f"in the with: {encoded_qrcode}")
            response = f"<div>Scan the QR-code with Google Autnentificator App</div><img src='data:image/png;base64,{encoded_qrcode}' alt='QR Code' />"
            customer.secret_for_2fa = secret_for_2fa
            customer.save()
            os.remove(qr_file_path)
    else:
        response = "<div>Try again</div>"
    
    # return render(request, 'bank_app/customer_details.html', context)
    # print(os.path.exists(qr_file_path))
    # # file = Image.open(b(qr_file_path), "rb")
    # f = open(qr_file_path, "rb")
    # file = f.readline()
    # encoded_qrcode = base64.b64encode(file).decode("utf-8")
    # print(f"in the with: {encoded_qrcode}")
    #     # # With the secret, generate QR-code and send it to uesr 
    #     # totp = pyotp.TOTP('base32secret3232')
    #     # totp.now() # => '492039'
    #     # # OTP verified for current time
    #     # totp.verify('492039') # => True
    #     # totp.verify('492039') # => False

    
    # print("rm here")
    # print(os.path.exists(qr_file_path))
    # # os.system(f"rm {qr_file_path}")
    # # print(os.path.exists(qr_file_path))
    # print("rm there")
    return HttpResponse(response, content_type="text/plain")

@login_required
def generate_email_auth(request):
    print("In the generate_email_auth view")
    # assert hasattr(request.user, 'employee'), 'Customer user routing customer view.'
    employee = Employee.objects.get(user=request.user)
    context = {'employee': employee}
    
    secret_for_email_auth = pyotp.random_base32()
    # send_mail returns the number of successfully delivered messages (which can be 0 or 1 since it can only send one message).
    print("before response")
    employee_email = employee.user.email
    email_sent = send_mail(
                    'Bank Project -- Email 2-Factor Authentification',
                    'This email is a confirmation that 2-Factor Authentification on the "Bank Project" website was enabled.\n Next time you login, you will receive a code on this mailbox that will help you authentificate on the website',
                    'a.sandrovschii@gmail.com',
                    ['a.sandrovschii@gmail.com', employee_email],
                    fail_silently=False,
                )
    print("Email was sent: ", email_sent)
    # with mail.get_connection(fail_silently=False) as connection:
    #     mail.EmailMessage(
    #         'Subject here', 'Here is the message.', 'from@example.com', ['alex155@stud.kea.dk'],
    #         connection=connection,
    #     ).send()

    # print("connection", connection)
    response = ""
    if email_sent:
        employee.secret_for_email_auth = secret_for_email_auth
        employee.n_times_logged_in_with_email_auth = 0
        employee.save()
        response = f"<div>A confirmation email was sent to your {employee_email} mailbox.</div>"
    else:
        response = "<div>Try again</div>"
    return HttpResponse(response, content_type="text/plain")


@login_required
def check_2fa(request):
    customer = Customer.objects.get(user=request.user)
    customer_has_enabled_2fa = (len(str(customer.secret_for_2fa)) != 0)
    if (not customer_has_enabled_2fa):
         return HttpResponseRedirect(reverse('bank_app:index'))

    context = {}
    if request.method == "POST":
        code = request.POST['code']
        print("code", code)
        totp = pyotp.TOTP(customer.secret_for_2fa)
        is_code_correct = totp.verify(f'{code}') # => True
        print("is_code_correct", is_code_correct)
        if is_code_correct:
            return HttpResponseRedirect(reverse('bank_app:index'))
            # return HttpResponseRedirect(reverse('bank_app:check_2fa'))
        else:
            context = {
                'error': 'Incorrect code. Please try again'
            }
    return render(request, 'bank_app/check_2fa.html', context)
    
@login_required
def check_email_auth(request):
    print("in the check_email_auth")
    employee = Employee.objects.get(user=request.user)
    print("employee.secret_for_email_auth: ", employee.secret_for_email_auth)
    employee_has_enabled_email_auth = (employee.secret_for_email_auth is not None)
    print("employee_has_enabled_email_auth: ", employee_has_enabled_email_auth)
    if (not employee_has_enabled_email_auth):
         return HttpResponseRedirect(reverse('bank_app:index'))
    employee_email = employee.user.email
    context = {'employee_email': employee_email}
    hotp = pyotp.HOTP(employee.secret_for_email_auth)
    n_times_employee_logged_in_with_email_auth = employee.n_times_logged_in_with_email_auth
    print("n_times_employee_logged_in_with_email_auth: ", n_times_employee_logged_in_with_email_auth)
    correct_code = hotp.at(n_times_employee_logged_in_with_email_auth)
    print("correct_code", correct_code)
    if request.method == "POST":
        reveived_code = request.POST['code']
        print("reveived_code", reveived_code)
        if correct_code == reveived_code:
            employee.n_times_logged_in_with_email_auth = 1 + n_times_employee_logged_in_with_email_auth
            employee.save()
            return HttpResponseRedirect(reverse('bank_app:index'))
            # return HttpResponseRedirect(reverse('bank_app:check_2fa'))
        else:
            context = {
                'error': 'Incorrect code. Please try again'
            }
    response = send_mail(
        'Bank Project -- Authentification Code',
        f"Use the following code to login to the 'Bank Project' website\n {correct_code }",
        'a.sandrovschii@gmail.com',
        ['a.sandrovschii@gmail.com', employee_email],
        fail_silently=False,
    )
    print("email was sent: ", response)
    return render(request, 'bank_app/check_email_auth.html', context)


    
# @login_required
# def check_email_auth(request):
#     send_mail(
#             'Subject here',
#             'Here is the message.',
#             'from@example.com',
#             ['to@example.com'],
#             fail_silently=False,
#         )
#     context = {}

#     # if request.method == "POST":
#         # user = authenticate(
#         #     request, username=request.POST['user'], password=request.POST['password'])
#         # if True:
#         #     dj_login(request, user)
#         #     return HttpResponseRedirect(reverse('bank_app:check_2fa'))
#         # else:
#         #     context = {
#         #         'error': 'Bad username or password.'
#         #     }
#     return render(request, 'login_app/login.html', context)


   # with mail.get_connection(fail_silently=False) as connection:
    #     mail.EmailMessage(
    #         'Subject here', 'Here is the message.', 'from@example.com', ['alex155@stud.kea.dk'],
    #         connection=connection,
    #     ).send()

    # respones = send_mail(
    #                 'Subject here',
    #                 'Here is the message.',
    #                 'a.sandrovschii@gmail.com',
    #                 ['alex155r@stud.kea.dk'],
    #                 fail_silently=False,
    #             )
    # print(respones)