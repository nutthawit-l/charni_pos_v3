from django import forms

from .models import COUNTRY_CHOICES
from .models import Event


class EventForm(forms.ModelForm):
    name = forms.CharField(
        widget=forms.TextInput(
            attrs={"placeholder": "Enter event name", "class": "form-control"},
        ),
    )
    country = forms.CharField(
        widget=forms.Select(
            choices=COUNTRY_CHOICES,
            attrs={"class": "form-select"},
        ),
    )
    start_at = forms.DateTimeField(
        widget=forms.DateTimeInput(
            attrs={"type": "datetime-local", "class": "form-control"},
            format="%Y-%m-%dT%H:%M",
        ),
        input_formats=["%Y-%m-%dT%H:%M"],
    )
    end_at = forms.DateTimeField(
        widget=forms.DateTimeInput(
            attrs={"type": "datetime-local", "class": "form-control"},
            format="%Y-%m-%dT%H:%M",
        ),
        input_formats=["%Y-%m-%dT%H:%M"],
    )
    booth_cost = forms.DecimalField(
        widget=forms.NumberInput(
            attrs={"class": "form-control"},
        ),
    )
    travel_cost = forms.DecimalField(
        widget=forms.NumberInput(
            attrs={"class": "form-control"},
        ),
    )
    hotel_cost = forms.DecimalField(
        widget=forms.NumberInput(
            attrs={"class": "form-control"},
        ),
    )
    food_cost = forms.DecimalField(
        widget=forms.NumberInput(
            attrs={"class": "form-control"},
        ),
    )

    class Meta:
        model = Event
        fields = [
            "name",
            "country",
            "start_at",
            "end_at",
            "booth_cost",
            "travel_cost",
            "hotel_cost",
            "food_cost",
        ]
