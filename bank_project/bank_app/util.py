from faker import Faker
fake = Faker(['da_DK'])

def gen_ban():
    return fake.aba()

def gen_iban():
    return fake.iban()