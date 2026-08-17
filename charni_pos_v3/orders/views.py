from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.views import View
from django.views.generic.list import ListView

from charni_pos_v3.events.models import Event
from charni_pos_v3.products.mixins import ProductListQuerysetMixin
from charni_pos_v3.products.models import Category
from charni_pos_v3.products.models import Product

from .cart import change_quantity
from .cart import currency_for_event
from .cart import get_cart
from .cart import price_for_product
from .cart import save_cart


class OrderListView(LoginRequiredMixin, ProductListQuerysetMixin, ListView):
    model = Product
    template_name = "orders/order_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        shop = self.request.user.shop
        event = self._get_event(shop)

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

    def _get_event(self, shop_id):
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
            self._event = get_object_or_404(Event, pk=event_id, shop=shop_id)
            self.request.session["current_event_id"] = self._event.pk
        return self._event


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
