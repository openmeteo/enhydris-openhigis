from django.conf import settings


class OpenHiGISMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.openhigis = {"ows_url": settings.ENHYDRIS_OWS_URL}
        response = self.get_response(request)
        return response
