from django.urls import path
from . import views


app_name = 'bank_app'

urlpatterns = [
   path('index/', views.index, name='index'), # to access it: localhost:8000/bank/index/
   path('create_employee/', views.create_employee, name='create_employee'), # to access it: localhost:8000/bank/create_employee
   path('create_customer/', views.create_customer, name='create_customer'), # to access it: localhost:8000/bank/create_customer
   path('create_account/', views.create_account, name='create_account'), # to access it: localhost:8000/bank/create_account
]