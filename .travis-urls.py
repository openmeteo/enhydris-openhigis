from django.urls import include, path

from enhydris import urls as enhydris_urls
from enhydris_openhigis import urls as enhydris_openhigis_urls

urlpatterns = [
    path("openhigis/", include(enhydris_openhigis_urls)),
    path("", include(enhydris_urls)),
]
