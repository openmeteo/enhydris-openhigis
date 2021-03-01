from django.db import connection
from django.test import TestCase

from model_mommy import mommy

from enhydris import models as enhydris_models
from enhydris_openhigis import models


class EssentialTestsMixin:
    def test_rowcount(self):
        self.assertEqual(self.model.objects.count(), self.expected_count)

    def test_name(self):
        self.assertEqual(self.model.objects.first().name, self.expected_name)

    def test_code(self):
        self.assertEqual(self.model.objects.first().code, self.expected_code)

    def test_remarks(self):
        self.assertEqual(self.model.objects.first().remarks, self.expected_remarks)

    def test_geom_x(self):
        self.assertAlmostEqual(
            self.model.objects.first().geom.x, self.expected_x, places=5
        )

    def test_geom_y(self):
        self.assertAlmostEqual(
            self.model.objects.first().geom.y, self.expected_y, places=5
        )


class DeleteMixin:
    condition = "geographicalName='Attica'"

    def setUp(self):
        super().setUp()
        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM openhigis.{} WHERE {}".format(
                    self.view_name, self.condition
                )
            )

    def test_count(self):
        self.assertEqual(self.model.objects.count(), 0)


class SridMixin:
    condition = "geographicalName='Attica'"

    def setUp(self):
        super().setUp()
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT ST_X(geometry), ST_Y(geometry)
                FROM openhigis.{} WHERE {}
                """.format(
                    self.view_name, self.condition
                )
            )
            self.row = cursor.fetchone()

    def test_x(self):
        self.assertAlmostEqual(self.row[0], 500000.00, places=2)

    def test_y(self):
        self.assertAlmostEqual(self.row[1], 4000000.00, places=2)


class HydroNodeSetupInitialRowMixin:
    def setUp(self):
        super().setUp()
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO openhigis.HydroNode
                (geographicalName, hydroId, remarks, geometry, id, elevation)
                VALUES
                ('Attica', '06', 'Hello world', 'SRID=2100;POINT(500000 4000000)', 1901,
                 782.5)
                """
            )


class RiverBasinDistrictSetupInitialRowMixin:
    def setUp(self):
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO openhigis.RiverBasinDistrict
                (geographicalName, hydroId, remarks, geometry, id)
                VALUES
                ('Attica', '06', 'Hello world', 'SRID=2100;POINT(500000 4000000)', 1852)
                """
            )


class RiverBasinDistrictInsertTestCase(
    EssentialTestsMixin, RiverBasinDistrictSetupInitialRowMixin, TestCase
):
    model = models.RiverBasinDistrict
    view_name = "RiverBasinDistrict"
    expected_count = 1
    expected_name = "Attica"
    expected_code = "06"
    expected_remarks = "Hello world"
    expected_x = 24.00166
    expected_y = 36.14732


class RiverBasinDistrictUpdateTestCase(
    EssentialTestsMixin, RiverBasinDistrictSetupInitialRowMixin, TestCase
):
    model = models.RiverBasinDistrict
    view_name = "RiverBasinDistrict"
    expected_count = 1
    expected_name = "Epirus"
    expected_code = "08"
    expected_remarks = "Hello planet"
    expected_x = 24.59318
    expected_y = 40.65191

    def setUp(self):
        super().setUp()
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE openhigis.RiverBasinDistrict
                SET geographicalName='Epirus', hydroId='08', remarks='Hello planet',
                geometry='SRID=2100;POINT(550000 4500000)'
                WHERE geographicalName='Attica'
                """
            )


class RiverBasinDistrictDeleteTestCase(
    DeleteMixin, RiverBasinDistrictSetupInitialRowMixin, TestCase
):
    model = models.RiverBasinDistrict
    view_name = "RiverBasinDistrict"


class RiverBasinDistrictSridTestCase(
    SridMixin, RiverBasinDistrictSetupInitialRowMixin, TestCase
):
    model = models.RiverBasinDistrict
    view_name = "RiverBasinDistrict"


class RiverBasinSetupInitialRowMixin:
    def setUp(self):
        super().setUp()
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO openhigis.RiverBasin
                (geographicalName, hydroId, remarks, geometry, origin, basinOrder,
                    basinOrderScheme, basinOrderScope, meanSlope,
                    meanElevation, id, area, meanCN,
                    concentrationTime, watercourseMainLength, watercourseMainSlope,
                    outletElevation, outlet)
                VALUES
                ('Attica', '06', 'Hello world', 'SRID=2100;POINT(500000 4000000)',
                    'manMade', '18', 'strahler', 'go figure', 0.15, 200,
                    1851, 680, 17, 42, 27.7, 0.288, 289, 1901)
                """
            )
        self.expected_basin_id = models.RiverBasin.objects.first().id


class DrainageBasinSetupInitialRowMixin(
    RiverBasinSetupInitialRowMixin,
    HydroNodeSetupInitialRowMixin,
):
    def setUp(self):
        super().setUp()
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO openhigis.DrainageBasin
                (geographicalName, hydroId, remarks, geometry, origin, basinOrder,
                    basinOrderScheme, basinOrderScope, totalArea, meanSlope,
                    meanElevation, id, riverBasin, area, meanCN,
                    concentrationTime, watercourseMainLength, watercourseMainSlope,
                    outletElevation, outlet
                )
                VALUES
                ('Attica', '06', 'Hello world', 'SRID=2100;POINT(500000 4000000)',
                    'manMade', '18', 'strahler', 'go figure', 680, 0.15, 200,
                    1852, 1851, 680, 17, 42, 27.7, 0.288, 289, 1901)
                """
            )


class BasinsAdditionalTestsMixin:
    def test_man_made(self):
        self.assertEqual(self.model.objects.first().man_made, self.expected_man_made)

    def test_mean_slope(self):
        self.assertAlmostEqual(
            self.model.objects.first().mean_slope, self.expected_mean_slope
        )

    def test_mean_elevation(self):
        self.assertAlmostEqual(
            self.model.objects.first().mean_elevation, self.expected_mean_elevation
        )

    def test_area(self):
        self.assertAlmostEqual(self.model.objects.first().area, self.expected_area)

    def test_mean_cn(self):
        self.assertEqual(self.model.objects.first().mean_cn, self.expected_mean_cn)

    def test_concentration_time(self):
        self.assertAlmostEqual(
            self.model.objects.first().concentration_time,
            self.expected_concentration_time,
        )

    def test_outlet_id(self):
        self.assertEqual(self.model.objects.first().outlet_id, self.expected_outlet_id)

    def test_watercourse_main_length(self):
        self.assertAlmostEqual(
            self.model.objects.first().watercourse_main_length,
            self.expected_watercourse_main_length,
        )

    def test_watercourse_main_slope(self):
        self.assertAlmostEqual(
            self.model.objects.first().watercourse_main_slope,
            self.expected_watercourse_main_slope,
        )

    def test_outlet_elevation(self):
        self.assertAlmostEqual(
            self.model.objects.first().outlet_elevation,
            self.expected_outlet_elevation,
        )


class ImportedIdTestsMixin:
    def test_imported_id(self):
        self.assertEqual(
            self.model.objects.first().imported_id, self.expected_imported_id
        )


class HydroOrderTestsMixin:
    def test_hydro_order(self):
        self.assertEqual(
            self.model.objects.first().hydro_order, self.expected_hydro_order
        )

    def test_hydro_order_scheme(self):
        self.assertEqual(
            self.model.objects.first().hydro_order_scheme,
            self.expected_hydro_order_scheme,
        )

    def test_hydro_order_scope(self):
        self.assertEqual(
            self.model.objects.first().hydro_order_scope,
            self.expected_hydro_order_scope,
        )


class DrainageBasinAdditionalTestsMixin:
    def test_total_area(self):
        self.assertAlmostEqual(
            self.model.objects.first().total_area, self.expected_total_area
        )


class DrainageBasinInsertTestCase(
    EssentialTestsMixin,
    HydroOrderTestsMixin,
    DrainageBasinSetupInitialRowMixin,
    BasinsAdditionalTestsMixin,
    ImportedIdTestsMixin,
    DrainageBasinAdditionalTestsMixin,
    TestCase,
):
    model = models.DrainageBasin
    view_name = "DrainageBasin"
    expected_count = 1
    expected_name = "Attica"
    expected_code = "06"
    expected_remarks = "Hello world"
    expected_x = 24.00166
    expected_y = 36.14732
    expected_man_made = True
    expected_hydro_order = "18"
    expected_hydro_order_scheme = "strahler"
    expected_hydro_order_scope = "go figure"
    expected_total_area = 680
    expected_mean_slope = 0.15
    expected_mean_elevation = 200
    expected_imported_id = 1852
    expected_area = 680
    expected_mean_cn = 17
    expected_concentration_time = 42
    expected_watercourse_main_length = 27.7
    expected_watercourse_main_slope = 0.288
    expected_outlet_elevation = 289

    @property
    def expected_outlet_id(self):
        return models.HydroNode.objects.get(imported_id=1901).id


class DrainageBasinUpdateTestCase(
    EssentialTestsMixin,
    DrainageBasinSetupInitialRowMixin,
    BasinsAdditionalTestsMixin,
    ImportedIdTestsMixin,
    DrainageBasinAdditionalTestsMixin,
    TestCase,
):
    model = models.DrainageBasin
    view_name = "DrainageBasin"
    expected_count = 1
    expected_name = "Epirus"
    expected_code = "08"
    expected_remarks = "Hello planet"
    expected_x = 24.59318
    expected_y = 40.65191
    expected_man_made = False
    expected_hydro_order = "19"
    expected_hydro_order_scheme = "mahler"
    expected_hydro_order_scope = "go figure again"
    expected_total_area = 690
    expected_mean_slope = 0.16
    expected_mean_elevation = 300
    expected_imported_id = 1852
    expected_area = 681
    expected_mean_cn = 18
    expected_concentration_time = 43
    expected_watercourse_main_length = 27.8
    expected_watercourse_main_slope = 0.289
    expected_outlet_elevation = 290

    @property
    def expected_outlet_id(self):
        return models.HydroNode.objects.get(imported_id=1901).id

    def setUp(self):
        super().setUp()
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE openhigis.{}
                SET
                    geographicalName='Epirus',
                    hydroId='08',
                    remarks='Hello planet',
                    geometry='SRID=2100;POINT(550000 4500000)',
                    origin='natural',
                    basinOrder='19',
                    basinOrderScheme='mahler',
                    basinOrderScope='go figure again',
                    totalArea=690,
                    meanSlope=0.16,
                    meanElevation=300,
                    area=681,
                    meanCN=18,
                    concentrationTime=43,
                    watercourseMainlength=27.8,
                    watercourseMainSlope=0.289,
                    outletElevation=290,
                    outlet=1901
                WHERE geographicalName='Attica'
                """.format(
                    self.view_name
                )
            )


class DrainageBasinDeleteTestCase(
    DeleteMixin, DrainageBasinSetupInitialRowMixin, TestCase
):
    model = models.DrainageBasin
    view_name = "DrainageBasin"


class DrainageBasinSridTestCase(SridMixin, DrainageBasinSetupInitialRowMixin, TestCase):
    model = models.DrainageBasin
    view_name = "DrainageBasin"


class RiverBasinInsertTestCase(
    EssentialTestsMixin,
    RiverBasinSetupInitialRowMixin,
    HydroNodeSetupInitialRowMixin,
    BasinsAdditionalTestsMixin,
    ImportedIdTestsMixin,
    TestCase,
):
    model = models.RiverBasin
    view_name = "RiverBasin"
    expected_count = 1
    expected_name = "Attica"
    expected_code = "06"
    expected_remarks = "Hello world"
    expected_x = 24.00166
    expected_y = 36.14732
    expected_man_made = True
    expected_mean_slope = 0.15
    expected_mean_elevation = 200
    expected_imported_id = 1851
    expected_area = 680
    expected_mean_cn = 17
    expected_concentration_time = 42
    expected_watercourse_main_length = 27.7
    expected_watercourse_main_slope = 0.288
    expected_outlet_elevation = 289

    @property
    def expected_outlet_id(self):
        return models.HydroNode.objects.get(imported_id=1901).id

    model = models.RiverBasin
    view_name = "RiverBasin"


class RiverBasinUpdateTestCase(
    EssentialTestsMixin,
    RiverBasinSetupInitialRowMixin,
    HydroNodeSetupInitialRowMixin,
    BasinsAdditionalTestsMixin,
    ImportedIdTestsMixin,
    TestCase,
):
    model = models.RiverBasin
    view_name = "RiverBasin"
    expected_count = 1
    expected_name = "Epirus"
    expected_code = "08"
    expected_remarks = "Hello planet"
    expected_x = 24.59318
    expected_y = 40.65191
    expected_man_made = False
    expected_mean_slope = 0.16
    expected_mean_elevation = 300
    expected_imported_id = 1851
    expected_area = 681
    expected_mean_cn = 18
    expected_concentration_time = 43
    expected_watercourse_main_length = 27.8
    expected_watercourse_main_slope = 0.289
    expected_outlet_elevation = 290

    @property
    def expected_outlet_id(self):
        return models.HydroNode.objects.get(imported_id=1901).id

    def setUp(self):
        super().setUp()
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE openhigis.{}
                SET
                    geographicalName='Epirus',
                    hydroId='08',
                    remarks='Hello planet',
                    geometry='SRID=2100;POINT(550000 4500000)',
                    origin='natural',
                    basinOrder='19',
                    basinOrderScheme='mahler',
                    basinOrderScope='go figure again',
                    meanSlope=0.16,
                    meanElevation=300,
                    area=681,
                    meanCN=18,
                    concentrationTime=43,
                    watercourseMainlength=27.8,
                    watercourseMainSlope=0.289,
                    outletElevation=290,
                    outlet=1901
                WHERE geographicalName='Attica'
                """.format(
                    self.view_name
                )
            )


class RiverBasinDeleteTestCase(DeleteMixin, RiverBasinSetupInitialRowMixin, TestCase):
    model = models.RiverBasin
    view_name = "RiverBasin"


class RiverBasinSridTestCase(DrainageBasinSridTestCase):
    model = models.RiverBasin
    view_name = "RiverBasin"


class InsertEntityWithNullGeographicalNameTestCase(TestCase):
    def setUp(self):
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO openhigis.RiverBasinDistrict
                (geographicalName, hydroId, remarks, geometry, id)
                VALUES
                (NULL, '06', 'Hello world', 'SRID=2100;POINT(500000 4000000)', 1852)
                """
            )

    def test_name(self):
        self.assertEqual(models.RiverBasinDistrict.objects.first().name, "")


class StationBasinSetupInitialRowMixin(
    RiverBasinSetupInitialRowMixin, HydroNodeSetupInitialRowMixin
):
    def setUp(self):
        super().setUp()
        mommy.make(models.Station, id=1852, name="Χόμπιτον")
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO openhigis.StationBasin
                (geographicalName, hydroId, remarks, geometry, origin,
                    meanSlope, meanElevation, id, riverBasin,
                    basinOrder, basinOrderScheme, basinOrderScope, area, meanCN,
                    concentrationTime, watercourseMainLength, watercourseMainSlope,
                    stationElevation, outlet
                )
                VALUES
                ('Attica', '06', 'Hello world', 'SRID=2100;POINT(500000 4000000)',
                    'manMade', 0.15, 200, 1852, 1851, '18', 'strahler',
                    'go figure', 680, 17, 42, 27.7, 0.288, 289, 1901
                )
                """
            )


class StationBasinAdditionalTestsMixin:
    def test_area(self):
        self.assertAlmostEqual(
            models.StationBasin.objects.first().area, self.expected_area
        )

    def test_mean_cn(self):
        self.assertEqual(
            models.StationBasin.objects.first().mean_cn, self.expected_mean_cn
        )

    def test_concentration_time(self):
        self.assertAlmostEqual(
            models.StationBasin.objects.first().concentration_time,
            self.expected_concentration_time,
        )

    def test_outlet_id(self):
        self.assertEqual(
            models.StationBasin.objects.first().outlet_id, self.expected_outlet_id
        )

    def test_watercourse_main_length(self):
        self.assertAlmostEqual(
            models.StationBasin.objects.first().watercourse_main_length,
            self.expected_watercourse_main_length,
        )

    def test_watercourse_main_slope(self):
        self.assertAlmostEqual(
            models.StationBasin.objects.first().watercourse_main_slope,
            self.expected_watercourse_main_slope,
        )

    def test_outlet_elevation(self):
        self.assertAlmostEqual(
            models.StationBasin.objects.first().outlet_elevation,
            self.expected_outlet_elevation,
        )


class StationBasinInsertTestCase(
    EssentialTestsMixin,
    StationBasinSetupInitialRowMixin,
    BasinsAdditionalTestsMixin,
    HydroOrderTestsMixin,
    StationBasinAdditionalTestsMixin,
    TestCase,
):
    model = models.StationBasin
    view_name = "StationBasin"
    expected_count = 1
    expected_name = "Attica"
    expected_code = "06"
    expected_remarks = "Hello world"
    expected_x = 24.00166
    expected_y = 36.14732
    expected_man_made = True
    expected_mean_slope = 0.15
    expected_mean_elevation = 200
    expected_hydro_order = "18"
    expected_hydro_order_scheme = "strahler"
    expected_hydro_order_scope = "go figure"
    expected_area = 680
    expected_mean_cn = 17
    expected_concentration_time = 42
    expected_watercourse_main_length = 27.7
    expected_watercourse_main_slope = 0.288
    expected_outlet_elevation = 289

    @property
    def expected_outlet_id(self):
        return models.HydroNode.objects.get(imported_id=1901).id

    def test_geographical_name(self):
        with connection.cursor() as cursor:
            cursor.execute("SELECT geographicalName FROM openhigis.StationBasin")
            row = cursor.fetchone()
        self.assertEqual(row[0], "Λεκάνη ανάντη του σταθμού Χόμπιτον")


class StationBasinUpdateTestCase(
    EssentialTestsMixin,
    StationBasinSetupInitialRowMixin,
    HydroOrderTestsMixin,
    BasinsAdditionalTestsMixin,
    StationBasinAdditionalTestsMixin,
    TestCase,
):
    model = models.StationBasin
    view_name = "StationBasin"
    expected_count = 1
    expected_name = "Epirus"
    expected_code = "08"
    expected_remarks = "Hello planet"
    expected_x = 24.59318
    expected_y = 40.65191
    expected_man_made = False
    expected_mean_slope = 0.16
    expected_mean_elevation = 300
    expected_hydro_order = "19"
    expected_hydro_order_scheme = "mahler"
    expected_hydro_order_scope = "figure go"
    expected_area = 681
    expected_mean_cn = 18
    expected_concentration_time = 43
    expected_watercourse_main_length = 27.8
    expected_watercourse_main_slope = 0.289
    expected_outlet_elevation = 290

    @property
    def expected_outlet_id(self):
        return models.HydroNode.objects.get(imported_id=1901).id

    def setUp(self):
        super().setUp()
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE openhigis.{}
                SET
                    geographicalName='Epirus',
                    hydroId='08',
                    remarks='Hello planet',
                    geometry='SRID=2100;POINT(550000 4500000)',
                    origin='natural',
                    meanSlope=0.16,
                    meanElevation=300,
                    basinOrder=19,
                    basinOrderScheme='mahler',
                    basinOrderScope='figure go',
                    area=681,
                    meanCN=18,
                    concentrationTime=43,
                    watercourseMainlength=27.8,
                    watercourseMainSlope=0.289,
                    stationElevation=290,
                    outlet=1901
                WHERE remarks='Hello world'
                """.format(
                    self.view_name
                )
            )


class StationBasinDeleteTestCase(
    DeleteMixin, StationBasinSetupInitialRowMixin, TestCase
):
    model = models.StationBasin
    view_name = "StationBasin"
    condition = "remarks = 'Hello world'"


class StationBasinSridTestCase(SridMixin, StationBasinSetupInitialRowMixin, TestCase):
    model = models.StationBasin
    view_name = "StationBasin"
    condition = "remarks = 'Hello world'"


class HydroNodeAdditionalTestsMixin:
    def test_elevation(self):
        self.assertAlmostEqual(
            self.model.objects.first().altitude, self.expected_altitude
        )


class HydroNodeInsertTestCase(
    EssentialTestsMixin,
    HydroNodeAdditionalTestsMixin,
    HydroNodeSetupInitialRowMixin,
    TestCase,
):
    model = models.HydroNode
    view_name = "HydroNode"
    expected_count = 1
    expected_name = "Attica"
    expected_code = "06"
    expected_remarks = "Hello world"
    expected_x = 24.00166
    expected_y = 36.14732
    expected_altitude = 782.5


class HydroNodeUpdateTestCase(
    EssentialTestsMixin,
    HydroNodeAdditionalTestsMixin,
    HydroNodeSetupInitialRowMixin,
    TestCase,
):
    model = models.HydroNode
    view_name = "HydroNode"
    expected_count = 1
    expected_name = "Epirus"
    expected_code = "08"
    expected_remarks = "Hello planet"
    expected_x = 24.59318
    expected_y = 40.65191
    expected_altitude = 783.6

    def setUp(self):
        super().setUp()
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE openhigis.HydroNode
                SET geographicalName='Epirus', hydroId='08', remarks='Hello planet',
                geometry='SRID=2100;POINT(550000 4500000)', elevation=783.6
                WHERE geographicalName='Attica'
                """
            )


class HydroNodeDeleteTestCase(DeleteMixin, HydroNodeSetupInitialRowMixin, TestCase):
    model = models.HydroNode
    view_name = "HydroNode"


class HydroNodeSridTestCase(SridMixin, HydroNodeSetupInitialRowMixin, TestCase):
    model = models.HydroNode
    view_name = "HydroNode"
    condition = "remarks = 'Hello world'"


class WatercourseSetupInitialRowMixin(
    RiverBasinSetupInitialRowMixin, HydroNodeSetupInitialRowMixin
):
    def setUp(self):
        super().setUp()
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO openhigis.Watercourse
                (geographicalName, hydroId, remarks, geometry, origin, streamOrder,
                streamOrderScheme, streamOrderScope, id, localType, drainsBasin,
                width, delineationKnown, length, level, slope, levelOfDetail, outlet)
                VALUES
                ('Attica', '06', 'Hello world', 'SRID=2100;POINT(500000 4000000)',
                'manMade', '18', 'strahler', 'go figure', 1852, 'ditch', 1851, 2.718,
                TRUE, 3.14159, 776.3, 0.45, 50000, NULL)
                """
            )


class SurfaceWaterTestsMixin:
    def test_man_made(self):
        self.assertEqual(self.model.objects.first().man_made, self.expected_man_made)

    def test_local_type(self):
        self.assertEqual(
            self.model.objects.first().local_type, self.expected_local_type
        )

    def test_basin(self):
        self.assertEqual(
            self.model.objects.first().river_basin.id, self.expected_basin_id
        )

    def test_level_of_detail(self):
        self.assertEqual(
            self.model.objects.first().level_of_detail, self.expected_level_of_detail
        )


class WatercourseTestsMixin:
    def test_width(self):
        self.assertAlmostEqual(self.model.objects.first().width, self.expected_width)

    def test_delineation_known(self):
        self.assertEqual(
            self.model.objects.first().delineation_known,
            self.expected_delineation_known,
        )

    def test_length(self):
        self.assertAlmostEqual(self.model.objects.first().length, self.expected_length)

    def test_level(self):
        self.assertAlmostEqual(self.model.objects.first().level, self.expected_level)

    def test_outlet(self):
        self.assertEqual(self.model.objects.first().outlet_id, self.expected_outlet_id)

    def test_slope(self):
        self.assertEqual(self.model.objects.first().slope, self.expected_slope)


class WatercourseInsertTestCase(
    EssentialTestsMixin,
    HydroOrderTestsMixin,
    WatercourseSetupInitialRowMixin,
    SurfaceWaterTestsMixin,
    WatercourseTestsMixin,
    TestCase,
):
    model = models.Watercourse
    view_name = "Watercourse"
    expected_count = 1
    expected_name = "Attica"
    expected_code = "06"
    expected_remarks = "Hello world"
    expected_x = 24.00166
    expected_y = 36.14732
    expected_man_made = True
    expected_local_type = "ditch"
    expected_level_of_detail = 50000
    expected_width = 2.718
    expected_hydro_order = "18"
    expected_hydro_order_scheme = "strahler"
    expected_hydro_order_scope = "go figure"
    expected_start_node_id = None
    expected_delineation_known = True
    expected_length = 3.14159
    expected_level = 776.3
    expected_slope = 0.45
    expected_outlet_id = None


class WatercourseUpdateTestCase(
    EssentialTestsMixin,
    HydroOrderTestsMixin,
    WatercourseSetupInitialRowMixin,
    SurfaceWaterTestsMixin,
    WatercourseTestsMixin,
    TestCase,
):
    model = models.Watercourse
    view_name = "Watercourse"
    expected_count = 1
    expected_name = "Epirus"
    expected_code = "08"
    expected_remarks = "Hello planet"
    expected_x = 24.59318
    expected_y = 40.65191
    expected_man_made = False
    expected_local_type = "river"
    expected_width = 1.141
    expected_hydro_order = "19"
    expected_hydro_order_scheme = "mahler"
    expected_hydro_order_scope = "no figure"
    expected_level_of_detail = 100000
    expected_delineation_known = False
    expected_length = 3.13
    expected_level = 776.2
    expected_slope = 0.55

    @property
    def expected_outlet_id(self):
        return models.HydroNode.objects.get(imported_id=1901).id

    def setUp(self):
        super().setUp()
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE openhigis.{}
                SET
                geographicalName='Epirus',
                hydroId='08',
                remarks='Hello planet',
                geometry='SRID=2100;POINT(550000 4500000)',
                origin='natural',
                localType='river',
                width=1.141,
                levelOfDetail=100000,
                delineationKnown=FALSE,
                length=3.13,
                level=776.2,
                slope=0.55,
                streamOrder=19,
                streamOrderScheme='mahler',
                streamOrderScope='no figure',
                outlet=1901
                WHERE remarks='Hello world'
                """.format(
                    self.view_name
                )
            )


class WatercourseDeleteTestCase(DeleteMixin, WatercourseSetupInitialRowMixin, TestCase):
    model = models.Watercourse
    view_name = "Watercourse"
    condition = "remarks = 'Hello world'"


class WatercourseSridTestCase(SridMixin, WatercourseSetupInitialRowMixin, TestCase):
    model = models.Watercourse
    view_name = "Watercourse"
    condition = "remarks = 'Hello world'"


class NullLocalTypeTestCase(TestCase):
    def _create_row(self, local_type_sql_expression="NULL"):
        with connection.cursor() as cursor:
            cursor.execute(
                f"""
                INSERT INTO openhigis.Watercourse
                (localType, geographicalName, hydroId, remarks, geometry, origin,
                streamOrder, streamOrderScheme, streamOrderScope, id, drainsBasin,
                width, delineationKnown, length, level, slope, levelOfDetail, outlet)
                VALUES
                ({local_type_sql_expression}, 'Attica', '06', 'Hello world',
                'SRID=2100;POINT(500000 4000000)', 'manMade', '18', 'strahler',
                'go figure', 1852, 1851, 2.718, TRUE, 3.14159, 776.3, 0.45, 50000,
                NULL)
                """
            )

    def test_can_insert_null_local_type(self):
        self._create_row()
        self.assertEqual(models.Watercourse.objects.first().local_type, "")

    def test_can_update_with_null_local_type(self):
        self._create_row("'ditch'")
        with connection.cursor() as cursor:
            cursor.execute("UPDATE openhigis.Watercourse SET localType=NULL")
        self.assertEqual(models.Watercourse.objects.first().local_type, "")


class StandingWaterSetupInitialRowMixin(RiverBasinSetupInitialRowMixin):
    def setUp(self):
        super().setUp()
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO openhigis.StandingWater
                (geographicalName, hydroId, remarks, geometry, origin, id, localType,
                drainsBasin, elevation, meanDepth, levelOfDetail)
                VALUES
                ('Attica', '06', 'Hello world', 'SRID=2100;POINT(500000 4000000)',
                'manMade', 1852, 'pool', 1851, 784.1, 18.7, 50000)
                """
            )
        self.expected_surface_water_id = models.StandingWater.objects.first().id


class StandingWaterTestsMixin:
    def test_elevation(self):
        self.assertAlmostEqual(
            self.model.objects.first().elevation, self.expected_elevation
        )

    def test_mean_depth(self):
        self.assertAlmostEqual(
            self.model.objects.first().mean_depth, self.expected_mean_depth
        )


class StandingWaterInsertTestCase(
    EssentialTestsMixin,
    StandingWaterSetupInitialRowMixin,
    SurfaceWaterTestsMixin,
    StandingWaterTestsMixin,
    TestCase,
):
    model = models.StandingWater
    view_name = "StandingWater"
    expected_count = 1
    expected_name = "Attica"
    expected_code = "06"
    expected_remarks = "Hello world"
    expected_x = 24.00166
    expected_y = 36.14732
    expected_man_made = True
    expected_local_type = "pool"
    expected_level_of_detail = 50000
    expected_elevation = 784.1
    expected_mean_depth = 18.7


class StandingWaterUpdateTestCase(
    EssentialTestsMixin,
    StandingWaterSetupInitialRowMixin,
    SurfaceWaterTestsMixin,
    StandingWaterTestsMixin,
    TestCase,
):
    model = models.StandingWater
    view_name = "StandingWater"
    expected_count = 1
    expected_name = "Epirus"
    expected_code = "08"
    expected_remarks = "Hello planet"
    expected_x = 24.59318
    expected_y = 40.65191
    expected_man_made = False
    expected_local_type = "lake"
    expected_level_of_detail = 100000
    expected_elevation = 784.2
    expected_mean_depth = 18.8

    def setUp(self):
        super().setUp()
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE openhigis.{}
                SET
                geographicalName='Epirus',
                hydroId='08',
                remarks='Hello planet',
                geometry='SRID=2100;POINT(550000 4500000)',
                origin='natural',
                localType='lake',
                levelOfDetail=100000,
                elevation=784.2,
                meanDepth=18.8
                WHERE remarks='Hello world'
                """.format(
                    self.view_name
                )
            )


class StandingWaterDeleteTestCase(
    DeleteMixin, StandingWaterSetupInitialRowMixin, TestCase
):
    model = models.StandingWater
    view_name = "StandingWater"
    condition = "remarks = 'Hello world'"


class StandingWaterSridTestCase(SridMixin, StandingWaterSetupInitialRowMixin, TestCase):
    model = models.StandingWater
    view_name = "StandingWater"
    condition = "remarks = 'Hello world'"


class StationSetupInitialRowMixin(StandingWaterSetupInitialRowMixin):
    def setUp(self):
        super().setUp()
        self.station = mommy.make(
            enhydris_models.Station,
            id=42,
            name="Hobbiton",
            owner=mommy.make(enhydris_models.Organization, name="Hobbits, Inc"),
            code="BETA18",
            remarks="Hello world",
            geom="SRID=4326;POINT(24.1 38.2)",
        )
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO openhigis.Station (id, geometry, basin, surfacewater) "
                "VALUES (42, 'SRID=2100;POINT(500000 4000000)', 1851, 1852);"
            )


class StationAdditionalTestsMixin:
    def test_geom2100_x(self):
        self.assertAlmostEqual(
            self.model.objects.first().geom2100.x, self.expected_geom2100_x
        )

    def test_geom2100_y(self):
        self.assertAlmostEqual(
            self.model.objects.first().geom2100.y, self.expected_geom2100_y
        )

    def test_basin(self):
        self.assertEqual(self.model.objects.first().basin_id, self.expected_basin_id)

    def test_surface_water(self):
        self.assertEqual(
            self.model.objects.first().surface_water_id, self.expected_surface_water_id
        )


class StationInsertTestCase(
    EssentialTestsMixin,
    StationSetupInitialRowMixin,
    StationAdditionalTestsMixin,
    TestCase,
):
    model = models.Station
    view_name = "Station"
    expected_count = 1
    expected_name = "Hobbiton"
    expected_code = "BETA18"
    expected_remarks = "Hello world"
    expected_x = 24.1
    expected_y = 38.2
    expected_geom2100_x = 500000
    expected_geom2100_y = 4000000


class StationUpdateTestCase(
    EssentialTestsMixin,
    StationSetupInitialRowMixin,
    StationAdditionalTestsMixin,
    TestCase,
):
    model = models.Station
    view_name = "Station"
    expected_count = 1
    expected_name = "Hobbiton"
    expected_code = "BETA18"
    expected_remarks = "Hello world"
    expected_x = 24.1
    expected_y = 38.2
    expected_geom2100_x = 570000
    expected_geom2100_y = 4570000

    def setUp(self):
        super().setUp()
        with connection.cursor() as cursor:
            # Attributes stored in enhydris Gentity, Gpoint and Station should be
            # ignored; only the ones stored in openhigis Station should be updated.
            cursor.execute(
                """
                UPDATE openhigis.{}
                SET
                name='Epirus',
                hydroId='08',
                remarks='Hello planet',
                geometry='SRID=2100;POINT(570000 4570000)'
                WHERE remarks='Hello world'
                """.format(
                    self.view_name
                )
            )


class StationDeleteTestCase(DeleteMixin, StationSetupInitialRowMixin, TestCase):
    model = models.Station
    view_name = "Station"
    condition = "remarks = 'Hello world'"

    def test_enhydris_station_should_not_be_touched(self):
        self.assertEqual(enhydris_models.Station.objects.count(), 1)


class StationSridTestCase(SridMixin, StationSetupInitialRowMixin, TestCase):
    model = models.Station
    view_name = "Station"
    condition = "remarks = 'Hello world'"


class WatercourseLinkSetupInitialRowMixin(HydroNodeSetupInitialRowMixin):
    def setUp(self):
        super().setUp()
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO openhigis.WatercourseLink
                (id, geographicalName, hydroId, remarks, geometry, length,
                flowDirection, startNode, endNode, fictitious)
                VALUES (1852, 'Segment 18', 'S18', 'hello world',
                'SRID=2100;POINT(500000 4000000)', 3.14159, 'inDirection', NULL, 1901,
                False)
                """
            )


class WatercourseLinkTestsMixin:
    def test_length(self):
        self.assertAlmostEqual(self.model.objects.first().length, self.expected_length)

    def test_flow_direction(self):
        self.assertAlmostEqual(
            self.model.objects.first().flow_direction, self.expected_flow_direction
        )

    def test_start_node(self):
        self.assertEqual(
            self.model.objects.first().start_node_id, self.expected_start_node_id
        )

    def test_end_node(self):
        self.assertEqual(
            self.model.objects.first().end_node_id, self.expected_end_node_id
        )

    def test_fictitious(self):
        self.assertEqual(
            self.model.objects.first().fictitious, self.expected_fictitious
        )


class WatercourseLinkInsertTestCase(
    EssentialTestsMixin,
    WatercourseLinkSetupInitialRowMixin,
    WatercourseLinkTestsMixin,
    TestCase,
):
    model = models.WatercourseLink
    view_name = "WatercourseLink"
    expected_count = 1
    expected_name = "Segment 18"
    expected_code = "S18"
    expected_length = 3.14159
    expected_flow_direction = "inDirection"
    expected_remarks = "hello world"
    expected_x = 24.00166
    expected_y = 36.14732
    expected_fictitious = False
    expected_start_node_id = None

    @property
    def expected_end_node_id(self):
        return models.HydroNode.objects.get(imported_id=1901).id


class WatercourseLinkUpdateTestCase(
    EssentialTestsMixin,
    WatercourseLinkSetupInitialRowMixin,
    WatercourseLinkTestsMixin,
    TestCase,
):
    model = models.WatercourseLink
    view_name = "WatercourseLink"
    expected_count = 1
    expected_name = "Segment 19"
    expected_code = "S19"
    expected_length = 2.718
    expected_flow_direction = "inOppositeDirection"
    expected_remarks = "hello earth"
    expected_x = 24.59318
    expected_y = 40.65191
    expected_fictitious = True
    expected_end_node_id = None

    @property
    def expected_start_node_id(self):
        return models.HydroNode.objects.get(imported_id=1901).id

    def setUp(self):
        super().setUp()
        with connection.cursor() as cursor:
            cursor.execute(
                f"""
                UPDATE openhigis.{self.view_name}
                SET
                geographicalName='Segment 19',
                hydroId='S19',
                remarks='hello earth',
                geometry='SRID=2100;POINT(550000 4500000)',
                length=2.718,
                flowDirection='inOppositeDirection',
                startNode=1901,
                endNode=NULL,
                fictitious=True
                WHERE remarks='hello world'
                """
            )


class WatercourseLinkDeleteTestCase(
    DeleteMixin, WatercourseLinkSetupInitialRowMixin, TestCase
):
    model = models.WatercourseLink
    view_name = "WatercourseLink"
    condition = "remarks = 'hello world'"


class WatercourseLinkSridTestCase(
    SridMixin, WatercourseLinkSetupInitialRowMixin, TestCase
):
    model = models.WatercourseLink
    view_name = "WatercourseLink"
    condition = "remarks = 'hello world'"
