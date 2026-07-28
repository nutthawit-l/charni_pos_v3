from django.db import models

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

    def __str__(self):
        return self.name
