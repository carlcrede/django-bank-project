from django.db import models
import datetime
from django.utils import timezone
import uuid

class Notification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    is_read = models.BooleanField(default=False)
    message = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE)

    @property
    def was_received_today(self):
        return self.timestamp.date() == datetime.date.today()

    def toggle_read(id):
        notification = Notification.objects.get(id=id)
        notification.is_read = not notification.is_read
        notification.save()
        return notification
