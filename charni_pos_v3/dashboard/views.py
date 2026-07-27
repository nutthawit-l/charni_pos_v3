from django.views.generic.base import TemplateView

from charni_pos_v3.events.models import Event


class HomePageView(TemplateView):
    template_name = "dashboard/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["event_list"] = Event.objects.all()
        return context
