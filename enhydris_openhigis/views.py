from django.apps import apps
from django.conf import settings
from django.contrib.gis.db.models import Extent
from django.contrib.gis.geos import Point
from django.http import HttpResponse
from django.urls import reverse
from django.views.generic import TemplateView, View

from enhydris.views_common import ensure_extent_is_large_enough


class MapView(TemplateView):
    template_name = "enhydris_openhigis/map/main.html"

    def get_context_data(self, *args, **kwargs):
        result = super().get_context_data(*args, **kwargs)
        result["ows_url"] = getattr(
            settings, "ENHYDRIS_OWS_URL", "http://localhost/geoserver"
        )
        result["base_url"] = reverse("openhigis_map")
        return result


def get_all_geomodels():
    result = {
        model
        for model in apps.get_app_config("enhydris_openhigis").get_models()
        if _model_has_field(model, "geom2100")
    }
    result = _get_leaf_classes(result)
    return result


def _model_has_field(model, fieldname):
    fieldnames = {f.name for f in model._meta.get_fields()}
    return fieldname in fieldnames


def _get_leaf_classes(class_list):
    """Return a subset of class_list that only contains classes without subclasses.

    Returns a subset of class_list that does not contain classes that are inherited by
    other classes of class_list.
    """
    return {
        klass for klass in class_list if _class_has_no_subclasses(klass, class_list)
    }


def _class_has_no_subclasses(klass, class_list):
    return not any({issubclass(k, klass) for k in class_list if k != klass})


class SearchView(View):
    def get(self, request, *args, **kwargs):
        self.search_term = kwargs["search_term"]
        bb = self.get_bounding_box()
        return HttpResponse(" ".join(map(str, bb)), content_type="text/plain")

    def get_bounding_box(self):
        min_x, min_y, max_x, max_y = 1e9, 1e9, -1e9, -1e9
        for model in get_all_geomodels():
            extent = model.objects.filter(
                name__unaccent__icontains=self.search_term
            ).aggregate(Extent("geom2100"))["geom2100__extent"]
            if not extent:
                continue
            min_x = min(min_x, extent[0])
            min_y = min(min_y, extent[1])
            max_x = max(max_x, extent[2])
            max_y = max(max_y, extent[3])
        if (min_x, min_y, max_x, max_y) == (1e9, 1e9, -1e9, -1e9):
            return settings.ENHYDRIS_MAP_DEFAULT_VIEWPORT[:]
        extent = [min_x, min_y, max_x, max_y]
        self.transform_extent_to_wgs84(extent)
        ensure_extent_is_large_enough(extent)
        return extent

    def transform_extent_to_wgs84(self, extent):
        p1 = Point(*extent[:2], srid=2100)
        p1.transform(4326)
        p2 = Point(*extent[2:], srid=2100)
        p2.transform(4326)
        extent[:] = [p1.x, p1.y, p2.x, p2.y]
