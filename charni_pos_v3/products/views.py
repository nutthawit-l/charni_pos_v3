from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.urls import reverse
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.views.generic.list import ListView

from .forms import CategoryForm
from .forms import ProductForm
from .models import Category
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


class CategoryCreateView(CreateView):
    model = Category
    form_class = CategoryForm
    template_name = "products/category_form.html"

    def form_invalid(self, form):
        if self.request.headers.get("HX-Request") == "true":
            html = render_to_string(
                "products/partials/category_form_errors.html",
                {"form": form},
                request=self.request,
            )
            response = HttpResponse(html, status=422)
            response["HX-Retarget"] = "#category-modal-errors"
            response["HX-Reswap"] = "innerHTML"
            return response
        return super().form_invalid(form)  # full page -> re-render form

    def form_valid(self, form):
        self.object = form.save()
        if self.request.headers.get("HX-Request") == "true":
            html = render_to_string(
                "products/partials/category_option.html",
                {"category": self.object},
                request=self.request,
            )
            response = HttpResponse(html)
            response["HX-Trigger"] = "categoryCreated"
            return response
        return super().form_valid(form)  # full page -> redirect

    def get_success_url(self):
        back_url = self.request.POST.get("back") or self.request.GET.get("back")
        if back_url and back_url.startswith("/") and not back_url.startswith("//"):
            return back_url
        return reverse("products:product-create")


class ProductListView(LoginRequiredMixin, ListView):
    model = Product

    def get_queryset(self):
        return Product.objects.filter(shop=self.request.user.shop).select_related(
            "shop",
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        shop = self.request.user.shop
        context["shop_name"] = shop.name if shop else ""
        return context
