from django.urls import path
from . import views


app_name = 'bank_app'

urlpatterns = [
   path('index/', views.index, name='index'),
   path('create_employee/', views.create_employee, name='create_employee'),
   path('create_customer/', views.create_customer, name='create_customer'),
]