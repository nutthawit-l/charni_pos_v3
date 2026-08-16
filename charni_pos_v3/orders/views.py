from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Min
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.views.generic.list import ListView

from charni_pos_v3.events.models import Event
from charni_pos_v3.products.models import Category
from charni_pos_v3.products.models import Product


class OrderListView(LoginRequiredMixin, ListView):
    model = Product

    def get_queryset(self):
        sort_map = {
            "name": "name",
            "stock": "stock",
            "cost": "min_price",  # needs annotation
        }

        qs = Product.objects.filter(
            shop=self.request.user.shop,
        ).select_related(
            "shop",
            "category",
        )

        category_id = self.request.GET.get("category")
        if category_id:
            qs = qs.filter(category_id=category_id)

        sort = self.request.GET.get("sort", "name")
        direction = self.request.GET.get("direction", "asc")
        order_by = sort_map.get(sort, "name")
        if sort == "cost":
            qs = qs.annotate(min_price=Min("productprice__price"))
        if direction == "desc":
            order_by = f"-{order_by.lstrip('-')}"
        else:
            order_by = order_by.lstrip("-")

        return qs.order_by(order_by)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        shop = self.request.user.shop
        context["event"] = self._get_event(shop)
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
