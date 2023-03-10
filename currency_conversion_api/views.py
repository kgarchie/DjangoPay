from django.http import Http404
from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView
from .models import Currency
from .serializers import CurrencySerializer, ConvertedValueSerializer
from rest_framework.response import Response


# Create your views here.

class CurrencyConversion(APIView):
    amount = 0
    from_currency = None
    to_currency = None

    def convert(self):
        try:
            to_currency_value = Currency.objects.filter(code__exact=self.to_currency).first()
            return self.from_currency * to_currency_value
        except Currency.DoesNotExist:
            raise Http404

    def get(self, amount, from_currency, to_currency):
        self.to_currency = to_currency
        self.from_currency = from_currency
        converted_value = self.convert()
        serializer = ConvertedValueSerializer(converted_value)
        return Response(serializer.data)


class CurrencyList(APIView):
    def get(self):
        currencies = Currency.objects.all()
        serializer = CurrencySerializer(currencies, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CurrencySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
