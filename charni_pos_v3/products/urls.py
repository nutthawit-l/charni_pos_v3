from django.urls import path

from .views import CategoryCreateView
from .views import ProductCreateView
from .views import ProductListView

app_name = "products"
urlpatterns = [
    path("new/", ProductCreateView.as_view(), name="product-create"),
    path("categories/new/", CategoryCreateView.as_view(), name="category-create"),
    path("", ProductListView.as_view(), name="product-list"),
]
