from django.db import models

from charni_pos_v3.constants import CURRENCY_CHOICE
from charni_pos_v3.shops.models import Shop


class Category(models.Model):
    name = models.CharField()
    created_at = models.DateTimeField(auto_now_add=True)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField()
    image_url = models.CharField()
    stock = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class ProductPrice(models.Model):
    price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
    )
    currency_code = models.CharField(max_length=3, choices=CURRENCY_CHOICE)
    created_at = models.DateTimeField(auto_now_add=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
