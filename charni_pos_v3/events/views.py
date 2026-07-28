from django.views.generic.edit import CreateView

from .models import Event


class EventCreateView(CreateView):
    model = Event
    fields = "__all__"
