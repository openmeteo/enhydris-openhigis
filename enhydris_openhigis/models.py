from django.contrib.gis.db import models

from enhydris.models import Garea
from enhydris.models import Station as EnhydrisStation


class GGRS87Mixin(models.Model):
    """Geometry field in GGRS87.

    Geographical models inherit geom from gentity; that one is stored with srid=4326.
    However, for the objects in this app, we need to store geometries in 2100. We
    can't possibly transform them on the fly; this takes too much time (and might not
    be very reliable, as there are more than one algorithms for the transformation).

    In addition, for stations, we need two geometries: the one is the co-ordinates
    entered by the station's owner, and the other is the co-ordinates corrected by our
    GIS experts. We don't want to modify the owner's co-ordinates, so we need a second
    field, geom2100.

    For objects besides stations (such as water basins), we don't really need two
    geometries. Still, we can't possibly use 2100, a Greek co-ordinate system, in
    openmeteo.org, an international database; so Enhydris remains on 4326. In openhigis,
    however, we must use 2100. Gentity.geom is mandatory, so what we do is transform
    geom2100 to 4326 on the fly on save in order to also store it in Gentity.geom. This
    is done at the SQL view level (defined in create_views.sql).
    """

    geom2100 = models.GeometryField(srid=2100)

    class Meta:
        abstract = True


class Station(EnhydrisStation, GGRS87Mixin):
    pass


class RiverBasinDistrict(Garea, GGRS87Mixin):
    pass


class RiverBasin(Garea, GGRS87Mixin):
    pass
