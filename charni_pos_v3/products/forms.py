from django import forms

from .models import Category
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


class CategoryForm(forms.ModelForm):
    name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Enter category name",
                "class": "form-control",
            },
        ),
    )

    class Meta:
        model = Category
        fields = ["name", "shop"]
