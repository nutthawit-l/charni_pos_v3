from django import forms

from .models import Product


class ProductForm(forms.ModelForm):
    image_url = forms.ImageField()
    name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Enter product name",
                "class": "form-control",
            },
        ),
    )
    stock = forms.IntegerField(
        min_value=0,
        widget=forms.NumberInput(
            attrs={"class": "form-control"},
        ),
    )

    class Meta:
        model = Product
        fields = [
            "image_url",
            "name",
            "stock",
            "shop",
            "category",
        ]
