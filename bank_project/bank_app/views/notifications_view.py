from django.contrib.auth.decorators import login_required
from bank_app.models import Notification
from django.shortcuts import render


@login_required
def notifications(request):
    notifications = request.user.customer.notifications
    context = {'notifications': notifications}
    return render(request, 'bank_app/notifications.html', context)
import datetime

@login_required
def notifications_list(request):
    notifications = request.user.customer.notifications.order_by('-timestamp')
    todays_notifications = notifications.filter(timestamp__date=datetime.date.today())
    earlier_notifications = notifications.exclude(timestamp__date=datetime.date.today())
    context = {
        'todays_notifications': todays_notifications,
        'earlier_notifications': earlier_notifications
    }
    return render(request, 'bank_app/notifications_list.html', context)


@login_required
def toggle_read_notification(request):
    id = request.POST['notification_id']
    print("toggle_read_notification id: ", id)
    Notification.toggle_read(request.POST['notification_id'])
    notifications = request.user.customer.notifications
    context = {'notifications': notifications}
    return render(request, 'bank_app/notifications.html', context)
