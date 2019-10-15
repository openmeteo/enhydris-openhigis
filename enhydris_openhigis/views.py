from django.conf import settings
from django.views.generic import TemplateView


class MapView(TemplateView):
    template_name = "enhydris_openhigis/map/main.html"

    def get_context_data(self, *args, **kwargs):
        result = super().get_context_data(*args, **kwargs)
        result["ows_url"] = getattr(
            settings, "ENHYDRIS_OWS_URL", "http://localhost/geoserver"
        )
        return result
