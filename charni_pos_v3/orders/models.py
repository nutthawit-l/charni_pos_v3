from django.db import models

from charni_pos_v3.constants import CURRENCY_CHOICE
from charni_pos_v3.events.models import Event


class Order(models.Model):
    currency_code = models.CharField(max_length=3, choices=CURRENCY_CHOICE)
    number = models.PositiveIntegerField(null=True)
    total_income = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0,
    )
    total_product_sold = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)

    class Meta:
        unique_together = ["event", "number"]

    def __str__(self):
        return f"Order #{self.pk} ({self.event})"


class OrderItem(models.Model):
    quantity = models.PositiveIntegerField(default=1)
    price_per_unit = models.DecimalField(
        max_digits=8,
        decimal_places=2,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.PROTECT,
    )

    def __str__(self):
        return f"{self.product} x{self.quantity}"
