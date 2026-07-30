from django.urls import reverse
from django.urls import reverse_lazy
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView
from django.views.generic.edit import UpdateView

from .forms import EventForm
from .models import Event


class EventCreateView(CreateView):
    model = Event
    form_class = EventForm
    success_url = reverse_lazy("dashboard:home")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        back_url = self.request.GET.get("back")
        if back_url and back_url.startswith("/"):
            context["back_url"] = back_url
        else:
            context["back_url"] = reverse("dashboard:home")
        return context


class EventDetailView(DetailView):
    model = Event


class EventUpdateView(UpdateView):
    model = Event
    form_class = EventForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        back_url = self.request.GET.get("back")
        if back_url and back_url.startswith("/"):
            context["back_url"] = back_url
        else:
            context["back_url"] = reverse("dashboard:home")
        return context
