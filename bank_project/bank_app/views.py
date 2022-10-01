from django.shortcuts import render, reverse
from django.http import HttpResponseRedirect
from .models import Employee
from .models import Customer

def index(request):
    return render(request, 'bank_app/index.html', {})

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
