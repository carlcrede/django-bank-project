from django.shortcuts import get_object_or_404, render, reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required

from bank_app.models import Account


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
def account_details(request, ban):
    if hasattr(request.user, 'customer'):
        'Staff user routing customer view.'
        account = get_object_or_404(
            Account, customer=request.user.customer, pk=ban)
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