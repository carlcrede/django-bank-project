from django.urls import path
from . import views


app_name = 'bank_app'

urlpatterns = [
   path('', views.index, name='index'), # to access it: localhost:8000/bank/
   path('customer_dashboard/', views.customer_dashboard, name='customer_dashboard'), # to access it: localhost:8000/bank/customer_dashboard
   path('create_employee/', views.create_employee, name='create_employee'), # to access it: localhost:8000/bank/create_employee
   path('create_customer/', views.create_customer, name='create_customer'), # to access it: localhost:8000/bank/create_customer
   path('create_account/', views.create_account, name='create_account'), # to access it: localhost:8000/bank/create_account
]