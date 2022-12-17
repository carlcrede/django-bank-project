# Generated by Django 4.1.1 on 2022-12-03 12:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bank_app', '0011_customer_secret_for_2fa'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='n_times_logged_in_with_email_auth',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='employee',
            name='secret_for_email_auth',
            field=models.CharField(default=1, max_length=32),
            preserve_default=False,
        ),
    ]