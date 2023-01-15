# Generated by Django 4.1.1 on 2023-01-14 13:36

import django.core.validators
from django.db import migrations, models
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('bank_app', '0017_merge_0016_merge_20230107_2134_0016_notification'),
    ]

    operations = [
        migrations.AlterField(
            model_name='externaltransfer',
            name='amount',
            field=models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(0.0)]),
        ),
        migrations.AlterField(
            model_name='externaltransfer',
            name='idempotency_key',
            field=models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False, unique=True),
        ),
        migrations.AlterField(
            model_name='notification',
            name='timestamp',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
