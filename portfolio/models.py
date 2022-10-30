from django.db import models

# Create your models here.
class stocks(models.Model):
    stock_name = models.CharField(max_length=100)
    stock_price = models.DecimalField(decimal_places = 2, max_digits = 10)
    date = models.DateField()
