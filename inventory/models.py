from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=100)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    # AI uses this value automatically
    previous_sales = models.IntegerField(default=0)

    def __str__(self):
        return self.name