from django.apps import AppConfig
import redis, os
from django.conf import settings
from .util import register_bank_on_redis

class BankAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'bank_app'

    def ready(self) -> None:
        # contact redis to update this banks ip/url from the registration number key
        print(f'Registering bank {settings.BANK_REGISTRATION_NUMBER} in redis / bank registry')
        if not register_bank_on_redis():
            print('Registration failed')
        else:
            print('Registration completed')
