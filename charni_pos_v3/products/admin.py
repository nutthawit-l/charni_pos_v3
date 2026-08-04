from django.contrib import admin

from .models import Category
from .models import Product
from .models import ProductPrice

admin.site.register(Category)
admin.site.register(Product)
admin.site.register(ProductPrice)
