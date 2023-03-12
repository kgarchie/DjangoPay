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
            to_currency_value = Currency.objects.get(code=self.to_currency).value

            from_currency_value = Currency.objects.get(code=self.from_currency).value

            converted_value = self.amount * to_currency_value / from_currency_value

            return {'converted_value': converted_value}
        except Currency.DoesNotExist:
            return None

    def get(self, request, currency_from, currency_to, amount):
        self.to_currency = currency_to
        self.from_currency = currency_from
        self.amount = amount

        converted_value = self.convert()
        if converted_value is not None:
            serializer = ConvertedValueSerializer(converted_value)
            return Response(serializer.data)
        return Response(status=status.HTTP_400_BAD_REQUEST)


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
