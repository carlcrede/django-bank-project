# Generated by Django 4.1.1 on 2022-10-03 14:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bank_app', '0004_rename_user_employee_employee'),
    ]

    operations = [
        migrations.RenameField(
            model_name='employee',
            old_name='employee',
            new_name='user',
        ),
    ]