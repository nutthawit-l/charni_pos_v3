from django.urls import reverse
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView

from .forms import ProductForm
from .models import Product


class ProductCreateView(CreateView):
    model = Product
    form_class = ProductForm
    success_url = reverse_lazy("dashboard:home")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        back_url = self.request.GET.get("back")
        if back_url and back_url.startswith("/"):
            context["back_url"] = back_url
        else:
            context["back_url"] = reverse("dashboard:home")
        return context
