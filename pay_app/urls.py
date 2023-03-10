from django.urls import path
from . import views

app_name = 'pay_app'

urlpatterns = [
    path('', views.index, name='index'),
    path('make-payment/', views.make_payment, name='make-payment'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('login/', views.login, name='login'),
]
