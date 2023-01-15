from faker import Faker
import os, redis
from django.conf import settings
fake = Faker(['da_DK'])

def gen_ban():
    return fake.aba()

def gen_iban():
    return fake.iban()

def redis_connect():
    host = os.environ['REDIS_HOST']
    port = os.environ['REDIS_PORT']
    password = os.environ['REDIS_PASSWORD']
    r = redis.Redis(host=host, port=port, password=password)
    return r

def register_bank_on_redis():
    bank_reg_nr = settings.BANK_REGISTRATION_NUMBER
    bank_url = settings.BANK_URL
    r = redis_connect()
    return r.set(name=bank_reg_nr, value=bank_url)

def get_external_bank_url(registration_number):
    res = redis_connection.get(registration_number)
    if res:
        return res.decode()
    return res

redis_connection = redis_connect()