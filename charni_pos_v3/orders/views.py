from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.http import Http404
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.views import View
from django.views.generic.list import ListView

from charni_pos_v3.events.models import Event
from charni_pos_v3.products.mixins import ProductListQuerysetMixin
from charni_pos_v3.products.models import Category
from charni_pos_v3.products.models import Product

from .cart import change_quantity
from .cart import clear_cart
from .cart import currency_for_event
from .cart import get_cart
from .cart import price_for_product
from .cart import save_cart
from .models import Order
from .models import OrderItem


class EventScopedMixin:
    """Resolve the ?event= query parameter agains the user's shop."""

    def get_event(self):
        if not hasattr(self, "_event"):
            event_id = self.request.GET.get("event")
            if not event_id:
                msg = "event query parameter is required"
                raise Http404(msg)
            try:
                event_id = int(event_id)
            except ValueError:
                msg = "event query parameter must be an integer"
                raise Http404(msg) from None
            self._event = get_object_or_404(
                Event,
                pk=event_id,
                shop=self.request.user.shop,
            )
            self.request.session["current_event_id"] = self._event.pk
        return self._event


class OrderListView(
    LoginRequiredMixin,
    EventScopedMixin,
    ProductListQuerysetMixin,
    ListView,
):
    model = Product
    template_name = "orders/order_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        shop = self.request.user.shop
        event = self.get_event()

        cart = get_cart(self.request)
        if cart["event_id"] != event.pk:
            cart = {"event_id": event.pk, "items": {}}
            save_cart(self.request, event, cart["items"])

        currency_code = currency_for_event(event)
        items = cart["items"]
        for product in context["object_list"]:
            product.cart_quantity = items.get(str(product.pk), 0)
            product.display_price = price_for_product(product, currency_code)

        context["event"] = event
        context["currency_code"] = currency_code
        context["cart_total_quantity"] = sum(items.values())
        context["shop_name"] = shop.name if shop else ""
        context["category_list"] = Category.objects.filter(shop=shop)
        context["active_category"] = self.request.GET.get("category", "")
        context["active_sort"] = self.request.GET.get("sort", "name")
        context["active_sort_direction"] = self.request.GET.get(
            "direction",
            "asc",
        )
        if context["active_sort_direction"] == "asc":
            context["toggle_sort_direction"] = "desc"
        else:
            context["toggle_sort_direction"] = "asc"
        return context


def _get_active_event(request):
    """Resolve the event the cart belongs to from session state."""
    event_id = request.session.get("current_event_id")
    if not event_id:
        msg = "no active event; open the order page with ?event= first"
        raise Http404(msg)
    return get_object_or_404(Event, pk=event_id, shop=request.user.shop)


def _get_cart_for_event(request, event):
    cart = get_cart(request)
    if cart["event_id"] != event.pk:
        return {"event_id": event.pk, "items": {}}
    return cart


def _cart_update_response(request, product, cart):
    html = render_to_string(
        "orders/partials/cart_controls.html",
        {"product": product, "quantity": cart["items"].get(str(product.pk), 0)},
        request=request,
    )
    html += render_to_string(
        "orders/partials/cart_checkout_btn.html",
        {
            "total_quantity": sum(cart["items"].values()),
            "oob": True,
        },
        request=request,
    )
    return HttpResponse(html)


class CartAddView(LoginRequiredMixin, View):
    def post(self, request, pk):
        product = get_object_or_404(Product, pk=pk, shop=request.user.shop)
        event = _get_active_event(request)
        cart = _get_cart_for_event(request, event)
        change_quantity(cart["items"], product, 1)
        save_cart(request, event, cart["items"])
        return _cart_update_response(request, product, cart)


class CartRemoveView(LoginRequiredMixin, View):
    def post(self, request, pk):
        product = get_object_or_404(Product, pk=pk, shop=request.user.shop)
        event = _get_active_event(request)
        cart = _get_cart_for_event(request, event)
        change_quantity(cart["items"], product, -1)
        save_cart(request, event, cart["items"])
        return _cart_update_response(request, product, cart)


class OrderCheckoutView(LoginRequiredMixin, View):
    def post(self, request):
        event = _get_active_event(request)
        cart = _get_cart_for_event(request, event)
        items = cart["items"]
        if not items:
            messages.error(request, "Your cart is empty.")
            return redirect(self._order_list_url(event))

        product_ids = []
        for key in items:
            try:
                product_ids.append(int(key))
            except TypeError, ValueError:
                continue

        products = list(
            Product.objects.filter(
                pk__in=product_ids,
                shop=request.user.shop,
            ).prefetch_related("productprice_set"),
        )

        if len(products) != len(product_ids):
            valid_keys = {str(product.pk) for product in products}
            cart["items"] = {
                key: quantity for key, quantity in items.items() if key in valid_keys
            }
            save_cart(request, event, cart["items"])
            msg = "Some products are no longer available: place review your cart."
            messages.error(request, msg)
            return redirect(self._order_list_url(event))

        currency_code = currency_for_event(event)
        total_income = Decimal("0")
        total_sold = 0
        with transaction.atomic():
            order = Order.objects.create(
                currency_code=currency_code,
                event=event,
            )
            for product in products:
                quantity = items[str(product.pk)]
                price = price_for_product(product, currency_code)
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    price_per_unit=price,
                )
                total_income += price * quantity
                total_sold += quantity
            order.total_income = total_income
            order.total_product_sold = total_sold
            order.save(update_fields=["total_income", "total_product_sold"])

        clear_cart(request)
        messages.success(
            request,
            f"Order #{order.pk} saved: {total_sold} item(s).",
        )
        return redirect(self._order_list_url(event))

    def _order_list_url(self, event):
        return f"{reverse('orders:order-list')}?event={event.pk}"


class TransactionListView(LoginRequiredMixin, EventScopedMixin, ListView):
    model = Order
    template_name = "orders/transaction_list.html"

    def get_queryset(self):
        return (
            Order.objects.filter(event=self.get_event())
            .prefetch_related("orderitem_set__product")
            .order_by("-created_at")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        shop = self.request.user.shop
        context["event"] = self.get_event()
        context["shop_name"] = shop.name if shop else ""
        return context
