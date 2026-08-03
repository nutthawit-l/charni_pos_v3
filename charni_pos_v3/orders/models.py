from django.db import models

from charni_pos_v3.events.models import Event

CURRENCY_CHOICE = [
    ("THB", "THB"),
    ("SGD", "SGD"),
]


class Order(models.Model):
    currency_code = models.CharField(max_length=3, choices=CURRENCY_CHOICE)
    total_income = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
    )
    total_product_sold = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
