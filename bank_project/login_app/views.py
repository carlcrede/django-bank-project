from django.shortcuts import render, reverse
from django.contrib.auth import authenticate, login as dj_login, logout as dj_logout
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required

def login(request):
    if request.user.is_authenticated:
       return HttpResponseRedirect(reverse('bank_app:index'))
    
    context = {}

    if request.method == "POST":
        user = authenticate(
            request, username=request.POST['user'], password=request.POST['password'])
        if user:
            dj_login(request, user)
            if hasattr(request.user, 'employee'):
                return HttpResponseRedirect(reverse('bank_app:check_email_auth'))
            else:
                return HttpResponseRedirect(reverse('bank_app:check_2fa'))
        else:
            context = {
                'error': 'Bad username or password.'
            }
    return render(request, 'login_app/login.html', context)

@login_required
def logout(request):
    dj_logout(request)
    return HttpResponseRedirect(reverse('login_app:login'))
