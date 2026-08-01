from django.db import models
from django.urls import reverse

from charni_pos_v3.shops.models import Shop

COUNTRY_CHOICES = [
    ("TH", "Thailand"),
    ("SG", "Singapore"),
]


class Event(models.Model):
    name = models.CharField()
    country = models.CharField(
        max_length=2,
        choices=COUNTRY_CHOICES,
        default="TH",
    )
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    booth_cost = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
    )
    travel_cost = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
    )
    hotel_cost = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
    )
    food_cost = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("events:event-detail", kwargs={"pk": self.pk})
