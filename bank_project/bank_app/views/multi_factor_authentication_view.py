import pyotp
import os
import base64
import subprocess

from django.shortcuts import HttpResponse, render, reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail

from bank_app.models import Employee, Customer

@login_required
def enable_2fa(request):
    print("In the enable_2fa view")
    assert hasattr(
        request.user, 'customer'), 'Staff user routing customer view.'
    customer = Customer.objects.get(user=request.user)
    customer_has_enabled_2fa = (customer.secret_for_2fa is not None)
    print(customer_has_enabled_2fa)
    context = {'customer': customer, 'enabled_2fa': customer_has_enabled_2fa}
    return render(request, 'bank_app/enable_2fa.html', context)


@login_required
def enable_email_auth(request):
    print("In the enable_email_auth view")
    assert hasattr(
        request.user, 'employee'), 'Customer user routing customer view.'
    employee = Employee.objects.get(user=request.user)
    employee_email = employee.user.email
    employee_has_enabled_email_auth = (
        employee.secret_for_email_auth is not None)
    print(employee_has_enabled_email_auth)
    context = {'employee_email': employee_email,
               'enabled_email_auth': employee_has_enabled_email_auth}
    return render(request, 'bank_app/enable_email_auth.html', context)


@login_required
def generate_2fa(request):
    print("In the enable_2fa view")
    assert hasattr(
        request.user, 'customer'), 'Staff user routing customer view.'
    customer = Customer.objects.get(user=request.user)
    context = {'customer': customer}

    print("In the enable_2fa view > POST")
    secret_for_2fa = pyotp.random_base32()
    string_for_2fa = f"otpauth://totp/Bank%20Project:%20{customer.user.first_name}%20{customer.user.last_name}?secret={secret_for_2fa}&issuer=Bank%20Project"
    qr_file_path = f"./bank_app/qrcodes/{customer.user.first_name}-{customer.user.last_name}.txt"
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
        response = "<div>Problem generating the QR-code. Please try again later.</div>"

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
        response = f"<div>A confirmation email was sent to your {employee_email} mailbox.</div><div>Next time you login, you will use 2-Factor Authentication.</div>"
    else:
        response = "<div>Try again</div>"
    return HttpResponse(response, content_type="text/plain")


@login_required
def check_2fa(request):
    customer = Customer.objects.get(user=request.user)
    customer_has_enabled_2fa = (customer.secret_for_2fa is not None)
    print("customer_has_enabled_2fa: ", customer_has_enabled_2fa)
    print("customer.secret_for_2fa: ", customer.secret_for_2fa)
    if (not customer_has_enabled_2fa):
        return HttpResponseRedirect(reverse('bank_app:index'))

    context = {}
    if request.method == "POST":
        code = request.POST['code']
        print("code", code)
        totp = pyotp.TOTP(customer.secret_for_2fa)
        is_code_correct = totp.verify(f'{code}')  # => True
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
    employee_has_enabled_email_auth = (
        employee.secret_for_email_auth is not None)
    print("employee_has_enabled_email_auth: ", employee_has_enabled_email_auth)
    if (not employee_has_enabled_email_auth):
        return HttpResponseRedirect(reverse('bank_app:index'))
    employee_email = employee.user.email
    context = {'employee_email': employee_email}
    hotp = pyotp.HOTP(employee.secret_for_email_auth)
    n_times_employee_logged_in_with_email_auth = employee.n_times_logged_in_with_email_auth
    print("n_times_employee_logged_in_with_email_auth: ",
          n_times_employee_logged_in_with_email_auth)
    correct_code = hotp.at(n_times_employee_logged_in_with_email_auth)
    print("correct_code", correct_code)
    if request.method == "POST":
        reveived_code = request.POST['code']
        print("reveived_code", reveived_code)
        if correct_code == reveived_code:
            employee.n_times_logged_in_with_email_auth = 1 + \
                n_times_employee_logged_in_with_email_auth
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