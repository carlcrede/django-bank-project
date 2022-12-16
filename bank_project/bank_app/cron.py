from .models import Recurring_Payment

def pay_recurring_payments():
    Recurring_Payment.pay_recurring_payments_for_today()

