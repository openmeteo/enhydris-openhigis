from django.urls import path

from . import views

urlpatterns = [
    path(
        "search/<path:search_term>", views.SearchView.as_view(), name="openhigis_search"
    ),
]
