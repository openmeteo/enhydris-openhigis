from django.conf import settings
from django.utils import translation


class OpenHiGISMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        lang = translation.get_language()
        if lang != "el":
            lang = ""
        ows_url_base = settings.ENHYDRIS_OWS_URL
        if ows_url_base.endswith("/"):
            ows_url_base = ows_url_base[:-1]
        request.openhigis = {"ows_url": f"{ows_url_base}{lang}/openhigis.map"}
        response = self.get_response(request)
        return response
