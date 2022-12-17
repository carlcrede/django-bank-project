from .models import Recurring_Payment

def test_cron_job():
    response = Recurring_Payment.pay_recurring_payments_for_today()
    print(response)
