# Generated by Django 4.1.1 on 2022-12-08 09:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bank_app', '0012_employee_n_times_logged_in_with_email_auth_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='secret_for_2fa',
            field=models.CharField(max_length=32, null=True),
        ),
        migrations.AlterField(
            model_name='employee',
            name='n_times_logged_in_with_email_auth',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='employee',
            name='secret_for_email_auth',
            field=models.CharField(max_length=32, null=True),
        ),
    ]
