# Generated by Django 4.1.1 on 2022-10-03 21:42

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('bank_app', '0006_rename_account_id_ledger_account_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='account_uuid',
            field=models.UUIDField(default=uuid.uuid4, unique=True),
        ),
    ]
