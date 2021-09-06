from django.conf import settings
from django.utils import translation


class OpenHiGISMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        lang = translation.get_language()
        if lang != "el":
            lang = ""
        request.openhigis = {
            "ows_url": f"{settings.ENHYDRIS_OWS_URL}{lang}/openhigis.map"
        }
        response = self.get_response(request)
        return response
