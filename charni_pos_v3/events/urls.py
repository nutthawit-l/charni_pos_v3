from django.urls import path

from .views import EventCreateView
from .views import EventDetailView
from .views import EventUpdateView

app_name = "events"
urlpatterns = [
    path("new/", EventCreateView.as_view(), name="event-create"),
    path("<int:pk>/", EventDetailView.as_view(), name="event-detail"),
    path("<int:pk>/edit", EventUpdateView.as_view(), name="event-update"),
]
