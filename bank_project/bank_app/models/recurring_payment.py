from uuid import uuid4
from django.db import models, transaction
from  django.core.validators import MinValueValidator, MaxValueValidator
from datetime import datetime


class Recurring_Payment(models.Model):
    sender = models.ForeignKey('Customer', on_delete=models.CASCADE)
    sender_account = models.ForeignKey('Account', on_delete=models.CASCADE)
    receiver_account = models.ForeignKey('Account', on_delete=models.CASCADE)
    text = models.CharField(max_length=200, null=True)
    amount = models.DecimalField(decimal_places=2, max_digits=10)
    start_date = models.DateTimeField(null=True)
    end_date = models.DateTimeField(null=True)
    pay_once_per_n_days = models.IntegerField(null=True, validators=[MinValueValidator(1, message="Minimum value is 1"), MaxValueValidator(356, message="Maximum value is 365")])
    time_to_live = models.IntegerField(null=True, validators=[MinValueValidator(0), MaxValueValidator(356)])

    @classmethod
    def get_recurring_payments_for_today(cls):
        recurring_payments_for_today = cls.objects.filter(start_date__date=datetime.date()).filter(time_to_live__isnull=False)

        # get payments that are in the range start_date <= today and end_date >= today
        # if start_date > today --> ttl should be NULL (maybe have 0)
        # if end_date < today --> ttl should be NULL
        # if start_date == today --> ttl should be NULL
        # if end_date < today --> ttl should be NULL

        # 
        return recurring_payments_for_today

    @classmethod
    def check_status_for_recurring_payments(cls):
        try:
            recurring_payments_are_before_start_date = cls.objects.filter(start_date__gte=datetime.date()).filter(time_to_live__isnull=False)
            recurring_payments_are_past_end_date = cls.objects.filter(end_date__lte=datetime.date()).filter(time_to_live__isnull=False)
            # iterate through recurring payments and set time_to_live to Null
            recurring_payments_done_today = recurring_payments_are_before_start_date + recurring_payments_are_past_end_date
            # recurring_payments_done_today = cls.objects.filter(start_date__gte=datetime.date()).filter(end_date__lte=datetime.date()).filter(time_to_live__isnull=False)
            for payment in recurring_payments_done_today:
                payment.pause_recurring_payment
                payment.save()
            
            recurring_payments_starting_today = cls.objects.filter(start_date__date=datetime.date()).filter(time_to_live__isnull=True)
            for payment in recurring_payments_starting_today:
                payment.resume_recurring_payment
                payment.save()
            
            recurring_payments__with_ttl_expired = cls.objects.filter(start_date__date=datetime.date()).filter(time_to_live__exact=0)
            for payment in recurring_payments__with_ttl_expired:
                payment.resume_recurring_payment
                payment.save()

            return True
        except:
            return False
        # iterate through recurring payments where start_date == today and time_to_live is set to Null, and change to value of pay_once_per_n_days
    @classmethod
    def get_recurring_payments_by_customer(cls, customer):
        recurring_payments = cls.objects.filter(sender=customer)
        return recurring_payments
    # once the payments were done on the recurring_payments then do TTL - 1

    @property
    def pause_recurring_payment(self):
        try:
            self.time_to_live = None
            self.save()
            return True
        except:
            return False
    
    @property
    def resume_recurring_payment(self):
        try:
            with transaction.atomic():
                self.time_to_live = self.pay_once_per_n_days
                self.save()
            return True
        except:
            return False
    
    @property
    def update_recurring_payment(self, amount=None, text=None, start_date=None, end_date=None, pay_once_per_n_days=None):
        try:
            with transaction.atomic():
                if amount:
                    self.amount = amount
                if text:
                    self.text = text
                if start_date:
                    self.start_date = start_date
                    self.time_to_live = None
                if end_date:
                    self.end_date = end_date
                if pay_once_per_n_days:
                    self.pay_once_per_n_days = pay_once_per_n_days
                    self.time_to_live = pay_once_per_n_days
                self.save()
            return True
        except:
            return False

    @property
    def update_time_to_live(self):
        try:
            self.time_to_live -= 1
            self.save()
            return True
        except:
            return False

    @classmethod
    def pay_recurring_payments_for_today(cls):
        with transaction.atomic():
            status_checked = cls.check_status_for_recurring_payments()
            if (status_checked):
                recurring_payments_for_today = cls.get_recurring_payments_for_today()
                for payment_for_today in recurring_payments_for_today:
                    payment_for_today.update_time_to_live
                
                # add them to task queue and deledate to MAKE_TRANSFER or BANK_TO_BANK_TRANSFER 

    @classmethod
    def test(cls):
        print("inside Recurring Payment class")

# place recurring_payments into queue
# run check_status_for_recurring_payments
# run get_recurring_payments_due_today
# run update_time_to_live
# add them to task queue and deledate to MAKE_TRANSFER or BANK_TO_BANK_TRANSFER
# 