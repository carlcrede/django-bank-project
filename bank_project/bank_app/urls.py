from django.urls import path
from .views import notifications_view, shared_view, stocks_view, recurring_payments_view, multi_factor_authentication_view, loans_view, transfers_view, customers_view, employees_view
from .api import ExternalTransferComplete, ExternalTransferFailed, ExternalTransferList, ExternalTransferDetail, ExternalTransferConfirm
app_name = 'bank_app'

urlpatterns = [
   path('', shared_view.index, name='index'), # to access it: localhost:8000/bank/
   path('customer_dashboard/', customers_view.customer_dashboard, name='customer_dashboard'), # to access it: localhost:8000/bank/customer_dashboard
   path('employee_dashboard/', employees_view.employee_dashboard, name='employee_dashboard'), # to access it: localhost:8000/bank/employee_dashboard
   path('account_details/<str:ban>/', shared_view.account_details, name='account_details'),
   path('make_transfer/', transfers_view.make_transfer, name='make_transfer'),
   path('make_external_transfer/', transfers_view.make_external_transfer, name='make_external_transfer'),
   path('external_transfers_overview/', transfers_view.external_transfers_overview, name='external_transfers_overview'),
   path('loans/', loans_view.loans, name='loans'),
   path('get_loan/', loans_view.get_loan, name='get_loan'),
   path('pay_loan/', loans_view.pay_loan, name='pay_loan'),
   path('transaction_details/<uuid:transaction_id>', customers_view.transaction_details, name='transaction_details'),
   path('create_employee/', employees_view.create_employee, name='create_employee'), # to access it: localhost:8000/bank/create_employee
   path('create_customer/', employees_view.create_customer, name='create_customer'), # to access it: localhost:8000/bank/create_customer
   path('create_account/', employees_view.create_account, name='create_account'), # to access it: localhost:8000/bank/create_account
   path('create_customer_account/<str:customer_username>/', employees_view.create_customer_account, name='create_customer_account'), # to access it: localhost:8000/bank/create_customer_account
   path('rerank_customer/<str:customer_username>/', employees_view.rerank_customer, name='rerank_customer'), # to access it: localhost:8000/bank/rerank_customer
   path('customer_details/<str:customer_username>/', employees_view.customer_details, name='customer_details'), # to access it: localhost:8000/bank/customer_details
   path('enable_2fa/', multi_factor_authentication_view.enable_2fa, name='enable_2fa'), # to access it: localhost:8000/bank/enable_2fa
   path('generate_2fa/', multi_factor_authentication_view.generate_2fa, name='generate_2fa'), # to access it: localhost:8000/bank/generate_2fa
   path('check_2fa/', multi_factor_authentication_view.check_2fa, name='check_2fa'), # to access it: localhost:8000/bank/generate_2fa
   path('enable_email_auth/', multi_factor_authentication_view.enable_email_auth, name='enable_email_auth'), # to access it: localhost:8000/bank/enable_email_auth
   path('generate_email_auth/', multi_factor_authentication_view.generate_email_auth, name='generate_email_auth'), # to access it: localhost:8000/bank/generate_email_auth
   path('check_email_auth/', multi_factor_authentication_view.check_email_auth, name='check_email_auth'), # to access it: localhost:8000/bank/check_email_auth
   path('recurring_payments/', recurring_payments_view.recurring_payments, name='recurring_payments'), # to access it: localhost:8000/bank/recurring_payments
   path('add_recurring_payment/', recurring_payments_view.add_recurring_payment, name='add_recurring_payment'), # to access it: localhost:8000/bank/add_recurring_payment
   path('update_recurring_payment/<int:pk>', recurring_payments_view.update_recurring_payment, name='update_recurring_payment'), # to access it: localhost:8000/bank/update_recurring_payment
   path('delete_recurring_payment/<int:pk>', recurring_payments_view.delete_recurring_payment, name='delete_recurring_payment'), # to access it: localhost:8000/bank/delete_recurring_payment
   path('stocks/', stocks_view.stocks, name='stocks'), # to access it: localhost:8000/bank/delete_recurring_payment
   path('buy_stocks/', stocks_view.buy_stocks, name='buy_stocks'), # to access it: localhost:8000/bank/buy_stocks
   path('sell_stocks/', stocks_view.sell_stocks, name='sell_stocks'), # to access it: localhost:8000/bank/sell_stocks
   path('api/v1/transfer', ExternalTransferList.as_view()),
   path('api/v1/transfer/<uuid:pk>', ExternalTransferDetail.as_view()),
   path('api/v1/confirm/<uuid:pk>', ExternalTransferConfirm.as_view()),
   path('api/v1/complete/<uuid:pk>', ExternalTransferComplete.as_view()),
   path('api/v1/failed/<uuid:pk>', ExternalTransferFailed.as_view()),
   path('notifications/', notifications_view.notifications, name='notifications'),
   path('notifications_list/', notifications_view.notifications_list, name='notifications_list'),
   path('toggle_read_notification/', notifications_view.toggle_read_notification, name='toggle_read_notification'),
   ]