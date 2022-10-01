from django.shortcuts import render, reverse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as dj_login, logout as dj_logout
from django.http import HttpResponseRedirect


def login(request):
    context = {}

    if request.method == "POST":
        user = authenticate(
            request, username=request.POST['user'], password=request.POST['password'])
        if user:
            dj_login(request, user)
            return HttpResponseRedirect(reverse('bank_app:index'))
        else:
            context = {
                'error': 'Bad username or password.'
            }
    return render(request, 'login_app/login.html', context)


def logout(request):
    dj_logout(request)
    return render(request, 'login_app/login.html')
