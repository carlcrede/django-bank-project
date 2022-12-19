from .models import Recurring_Payment
from datetime import datetime


def pay_recurring_payments():
    response = Recurring_Payment.pay_recurring_payments_for_today()

    print("RAN CRON")
    print("now", datetime.now())
