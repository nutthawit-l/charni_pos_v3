from django.urls import path

from .views import CategoryCreateView
from .views import ProductCreateView
from .views import ProductListView
from .views import ProductStockAddView
from .views import ProductStockReduceView

app_name = "products"
urlpatterns = [
    path("new/", ProductCreateView.as_view(), name="product-create"),
    path("categories/new/", CategoryCreateView.as_view(), name="category-create"),
    path(
        "<int:pk>/stock/add/",
        ProductStockAddView.as_view(),
        name="product-stock-add",
    ),
    path(
        "<int:pk>/stock/reduce/",
        ProductStockReduceView.as_view(),
        name="product-stock-reduce",
    ),
    path("", ProductListView.as_view(), name="product-list"),
]
