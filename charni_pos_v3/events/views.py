from django.urls import reverse_lazy
from django.views.generic.edit import CreateView

from .forms import EventForm
from .models import Event


class EventCreateView(CreateView):
    model = Event
    form_class = EventForm
    success_url = reverse_lazy("dashboard:home")
