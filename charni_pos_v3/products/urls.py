from django.urls import path

from .views import ProductCreateView

app_name = "products"
urlpatterns = [
    path("new/", ProductCreateView.as_view(), name="product-create"),
]
