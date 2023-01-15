from django.urls import path
from . import views
from .api import ExternalTransferComplete, ExternalTransferFailed, ExternalTransferList, ExternalTransferDetail, ExternalTransferConfirm
app_name = 'bank_app'

urlpatterns = [
   path('', views.index, name='index'), # to access it: localhost:8000/bank/
   path('customer_dashboard/', views.customer_dashboard, name='customer_dashboard'), # to access it: localhost:8000/bank/customer_dashboard
   path('employee_dashboard/', views.employee_dashboard, name='employee_dashboard'), # to access it: localhost:8000/bank/employee_dashboard
   path('account_details/<str:ban>/', views.account_details, name='account_details'),
   path('make_transfer/', views.make_transfer, name='make_transfer'),
   path('make_external_transfer/', views.make_external_transfer, name='make_external_transfer'),
   path('get_loan/', views.get_loan, name='get_loan'),
   path('pay_loan/', views.pay_loan, name='pay_loan'),
   path('transaction_details/<uuid:transaction_id>', views.transaction_details, name='transaction_details'),
   path('create_employee/', views.create_employee, name='create_employee'), # to access it: localhost:8000/bank/create_employee
   path('create_customer/', views.create_customer, name='create_customer'), # to access it: localhost:8000/bank/create_customer
   path('create_account/', views.create_account, name='create_account'), # to access it: localhost:8000/bank/create_account
   path('create_customer_account/<str:customer_username>/', views.create_customer_account, name='create_customer_account'), # to access it: localhost:8000/bank/create_customer_account
   path('rerank_customer/<str:customer_username>/', views.rerank_customer, name='rerank_customer'), # to access it: localhost:8000/bank/rerank_customer
   path('customer_details/<str:customer_username>/', views.customer_details, name='customer_details'), # to access it: localhost:8000/bank/customer_details
   path('enable_2fa/', views.enable_2fa, name='enable_2fa'), # to access it: localhost:8000/bank/enable_2fa
   path('generate_2fa/', views.generate_2fa, name='generate_2fa'), # to access it: localhost:8000/bank/generate_2fa
   path('check_2fa/', views.check_2fa, name='check_2fa'), # to access it: localhost:8000/bank/generate_2fa
   path('enable_email_auth/', views.enable_email_auth, name='enable_email_auth'), # to access it: localhost:8000/bank/enable_email_auth
   path('generate_email_auth/', views.generate_email_auth, name='generate_email_auth'), # to access it: localhost:8000/bank/generate_email_auth
   path('check_email_auth/', views.check_email_auth, name='check_email_auth'), # to access it: localhost:8000/bank/check_email_auth
   path('recurring_payments/', views.recurring_payments, name='recurring_payments'), # to access it: localhost:8000/bank/recurring_payments
   path('add_recurring_payment/', views.add_recurring_payment, name='add_recurring_payment'), # to access it: localhost:8000/bank/add_recurring_payment
   path('update_recurring_payment/<int:pk>', views.update_recurring_payment, name='update_recurring_payment'), # to access it: localhost:8000/bank/update_recurring_payment
   path('delete_recurring_payment/<int:pk>', views.delete_recurring_payment, name='delete_recurring_payment'), # to access it: localhost:8000/bank/delete_recurring_payment
   path('api/v1/transfer', ExternalTransferList.as_view()),
   path('api/v1/transfer/<uuid:pk>', ExternalTransferDetail.as_view()),
   path('api/v1/confirm/<uuid:pk>', ExternalTransferConfirm.as_view()),
   path('api/v1/complete/<uuid:pk>', ExternalTransferComplete.as_view()),
   path('api/v1/failed/<uuid:pk>', ExternalTransferFailed.as_view()),
   path('notifications/', views.notifications, name='notifications'),
   path('notifications_list/', views.notifications_list, name='notifications_list'),
   path('toggle_read_notification/', views.toggle_read_notification, name='toggle_read_notification'),
   ]