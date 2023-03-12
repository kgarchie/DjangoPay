from django.urls import path
from . import views, \
    converters  # important, otherwise the converter won't work to convert the amount in the url to float

app_name = 'currency_conversion_api'

urlpatterns = [
    path('conversion/<str:currency_from>/<str:currency_to>/<float:amount>', views.CurrencyConversion.as_view()),
]
