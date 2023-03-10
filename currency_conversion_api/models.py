from django.db import models


# Create your models here.

class Currency(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=100)
    value = models.FloatField()

    def __str__(self):
        return self.name + ' ' + self.code + ' ' + self.value.__str__()
