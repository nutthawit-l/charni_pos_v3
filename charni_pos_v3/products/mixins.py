from django.db.models import Min

from charni_pos_v3.products.models import Product


class ProductListQuerysetMixin:
    """Shared category filtering and sorting for product list pages."""

    def get_queryset(self):
        sort_map = {
            "name": "name",
            "stock": "stock",
            "cost": "min_price",  # needs annotation
        }

        qs = (
            Product.objects.filter(
                shop=self.request.user.shop,
            )
            .select_related(
                "shop",
                "category",
            )
            .prefetch_related("productprice_set")
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
