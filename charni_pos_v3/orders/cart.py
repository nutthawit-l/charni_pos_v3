from __future__ import annotations

from decimal import Decimal
from typing import TypedDict

CART_SESSION_KEY = "cart"

# Event.country --> currency code used for prices and orders
COUNTRY_CURRENCY = {
    "TH": "THB",
    "SG": "SGD",
}


class Cart(TypedDict):
    event_id: int | None
    items: dict[str, int]


def get_cart(request) -> Cart:
    """Return the sanitized session cart.

    Shape: {"event_id": int | None, "items": {str(product_pk): int}}
    """
    raw = request.session.get(CART_SESSION_KEY)
    if not isinstance(raw, dict):
        raw = {}

    # Get event_id from cart in session
    raw_event_id = raw.get("event_id")
    event_id = raw_event_id if isinstance(raw_event_id, int) else None

    raw_items = raw.get("items")
    sanitized_items: dict[str, int] = {}

    # Get items from session cart and build sanitized_items dict.
    # Returns an empty dict if session cart has no items.
    if isinstance(raw_items, dict):
        for key, value in raw_items.items():
            try:
                quantity = int(value)
            except TypeError, ValueError:
                continue

            if quantity > 0:
                sanitized_items[str(key)] = quantity

    return {
        "event_id": event_id,
        "items": sanitized_items,
    }


def save_cart(request, event, items):
    request.session[CART_SESSION_KEY] = {
        "event_id": event.pk,
        "items": items,
    }


def currency_for_event(event):
    return COUNTRY_CURRENCY.get(event.country, "THB")


def price_for_product(product, currency_code) -> Decimal:
    """Best price in the given currency,
    falling back to the lowest price.
    """
    prices = list(product.productprice_set.all())
    for price in prices:
        if price.currency_code == currency_code:
            return price.price
    return Decimal("0")


def change_quantity(items, product, amount):
    """Adjust a product quantity in ``items``, removing it at zero."""
    key = str(product.pk)
    quantity = items.get(key, 0) + amount
    if quantity > 0:
        items[key] = quantity
    else:
        items.pop(key, None)
