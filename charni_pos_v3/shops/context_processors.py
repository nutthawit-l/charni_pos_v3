def shop_name(request):
    user = getattr(request, "user", None)
    if user is None or not user.is_authenticated:
        return {"shop_name": ""}
    shop = getattr(user, "shop", None)
    return {"shop_name": shop.name if shop else ""}
