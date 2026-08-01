from django import forms

from .models import Shop


class ShopForm(forms.ModelForm):
    name = forms.CharField(
        widget=forms.TextInput(
            attrs={"placeholder": "Enter shop name", "class": "form-control"},
        ),
    )

    class Meta:
        model = Shop
        fields = ["name"]
