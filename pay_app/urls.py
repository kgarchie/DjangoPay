from django.urls import path
from . import views

app_name = 'pay_app'

urlpatterns = [
    path('', views.index, name='index'),
    path('make-payment/', views.make_payment, name='make-payment'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('register/', views.register, name='register'),
    path('notifications/', views.notifications, name='notifications'),
    path('notification/<int:notification_id>/read/', views.notifications, name='notification'),
    path('accept-payment/<int:notification_id>/', views.accept_payment, name='accept-payment'),
    path('reject-payment/<int:notification_id>/', views.reject_payment, name='reject-payment'),
    path('success/', views.success, name='success'),
    path('request-payment/', views.request_payment, name='request-payment'),
    path('success/', views.success, name='success'),
]
