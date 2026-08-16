from charni_pos_v3.events.models import Event


def current_event(request):
    user = getattr(request, "user", None)
    if user is None or not user.is_authenticated:
        return {"current_event": None}
    event_id = request.session.get("current_event_id")
    if not event_id:
        return {"current_event": None}
    return {
        "current_event": Event.objects.filter(
            pk=event_id,
            shop=user.shop,
        ).first(),
    }
