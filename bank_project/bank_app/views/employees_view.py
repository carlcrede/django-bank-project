from django.shortcuts import get_object_or_404, render, reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required

from bank_app.models import Employee, Customer

@login_required
def employee_dashboard(request):
    assert hasattr(
        request.user, 'employee'), 'Staff user routing customer view.'

    customers = Customer.objects.all()
    context = {
        'customers': customers,
    }
    return render(request, 'bank_app/employee_dashboard.html', context)

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
            Employee.create_employee(
                first_name, last_name, email, user_name, password)
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
            Employee.create_customer(
                first_name, last_name, email, user_name, phone, rank, password)
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