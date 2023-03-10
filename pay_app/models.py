from django.db import models
from django.contrib.auth.models import User as DjangoUser
import uuid


# Create your models here.

class User(DjangoUser):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    balance = models.IntegerField(default=10000)

    def __str__(self):
        return self.username + ' ' + str(self.balance)


class Transaction(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    money_from = models.ForeignKey(User, on_delete=models.CASCADE, related_name='money_from')
    money_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='money_to')
    amount = models.IntegerField()
    status = models.BooleanField(default=False)  # Internal status of the transaction, can be revoked by admin
    committed = models.BooleanField(default=False)  # True if transaction is accepted by the receiver
    transaction_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.uuid


class Notification(models.Model):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.CharField(max_length=100)
    read = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message
