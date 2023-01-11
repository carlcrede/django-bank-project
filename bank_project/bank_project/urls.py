from django.contrib import admin
from django.urls import path, include
# import notifications.urls
# from django.conf.urls import url

urlpatterns = [
    path('admin/', admin.site.urls),
    path('bank/', include('bank_app.urls')),
    path('accounts/', include('login_app.urls')),
    # url('^inbox/notifications/', include(notifications.urls, namespace='notifications')),
]