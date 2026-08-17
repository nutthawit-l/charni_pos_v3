from django.urls import path

from .views import CartAddView
from .views import CartRemoveView
from .views import OrderCheckoutView
from .views import OrderListView

app_name = "orders"
urlpatterns = [
    path("cart/add/<int:pk>/", CartAddView.as_view(), name="cart-add"),
    path("cart/remove/<int:pk>/", CartRemoveView.as_view(), name="cart-remove"),
    path("checkout/", OrderCheckoutView.as_view(), name="checkout"),
    path("", OrderListView.as_view(), name="order-list"),
]
