from django.contrib.gis.db import models

from enhydris.models import Garea, Gentity, Gpoint
from enhydris.models import Station as EnhydrisStation


class ImportedIdMixin(models.Model):
    """Extra id field.

    Gentities already have an id, which is given internally by Enhydris. This is
    insufficient for geographical data, which are imported in PostGIS from external
    files. Relationships already exist in these external files, and they are based on
    an id. It's hard to import these relationships if that id is thrown away, so we
    keep it.

    However, after the import is complete, this id is generally not necessary.
    """

    imported_id = models.IntegerField(unique=True)

    class Meta:
        abstract = True


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


class HydroOrderCodeMixin(models.Model):
    """INSPIRE data specification on hydrography, 5.5.2.2.1 (p. 57).
    """

    hydro_order = models.CharField(max_length=50, blank=True)
    hydro_order_scheme = models.CharField(max_length=50, blank=True)
    hydro_order_scope = models.CharField(max_length=50, blank=True)

    class Meta:
        abstract = True


class Station(EnhydrisStation, GGRS87Mixin):
    basin = models.ForeignKey("Basin", on_delete=models.CASCADE, null=True, blank=True)
    surface_water = models.ForeignKey(
        "SurfaceWater", on_delete=models.CASCADE, null=True, blank=True
    )


class RiverBasinDistrict(Garea, GGRS87Mixin, ImportedIdMixin):
    pass


class BasinMixin(models.Model):
    """Base class for drainage basins and river basins.

    INSPIRE uses the term "drainage basin" both for river basins and subbasins; a river
    basin is thus a subclass of drainage basin. However, it doesn't seem to provide an
    easy way to refer to subbasins, i.e. those drainage basins that are not river
    basins.

    Here we use "drainage basin" for sub-basins only. River basins and drainage basins
    have almost identical attributes (one exception is that drainage basins have a
    river_basin foreign key). This class (BasinMixin) contains common fields.
    """

    man_made = models.BooleanField(blank=True, null=True)
    mean_slope = models.FloatField(blank=True, null=True)
    mean_elevation = models.FloatField(blank=True, null=True)

    class Meta:
        abstract = True


class Basin(Garea, GGRS87Mixin, ImportedIdMixin, BasinMixin):
    pass


class RiverBasin(Basin):
    pass


class DrainageBasin(Basin, HydroOrderCodeMixin):
    """A subbasin.

    We use the term "DrainageBasin" differently from INSPIRE. Read the "BasinMixin"
    above for an explanation.
    """

    total_area = models.FloatField(blank=True, null=True)
    river_basin = models.ForeignKey(RiverBasin, on_delete=models.CASCADE)


class StationBasin(Garea, GGRS87Mixin, BasinMixin):
    """A subbasin defined by a measuring station."""

    river_basin = models.ForeignKey(RiverBasin, on_delete=models.CASCADE)
    station = models.ForeignKey(Station, on_delete=models.CASCADE)


class SurfaceWater(Gentity, GGRS87Mixin, ImportedIdMixin):
    """Base class for rivers (Watercourse) and lakes (StandingWater)."""

    local_type = models.CharField(max_length=50)
    man_made = models.BooleanField(blank=True, null=True)
    river_basin = models.ForeignKey(
        RiverBasin, on_delete=models.CASCADE, null=True, blank=True
    )


class HydroNode(Gpoint, GGRS87Mixin, ImportedIdMixin):
    pass


class Watercourse(SurfaceWater, HydroOrderCodeMixin):
    min_width = models.FloatField(blank=True, null=True)
    max_width = models.FloatField(blank=True, null=True)
    start_node = models.ForeignKey(
        HydroNode,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="watercourses_starting",
    )
    end_node = models.ForeignKey(
        HydroNode,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="watercourses_ending",
    )


class StandingWater(SurfaceWater):
    elevation = models.FloatField(blank=True, null=True)
    mean_depth = models.FloatField(blank=True, null=True)
