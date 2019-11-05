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
    def setUp(self):
        super().setUp()
        with connection.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM openhigis.{}
                WHERE geographicalName='Attica'
                """.format(
                    self.view_name
                )
            )

    def test_count(self):
        self.assertEqual(self.model.objects.count(), 0)


class SridMixin:
    def setUp(self):
        super().setUp()
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT ST_X(geometry), ST_Y(geometry)
                FROM openhigis.{} WHERE geographicalName='Attica'
                """.format(
                    self.view_name
                )
            )
            self.row = cursor.fetchone()

    def test_x(self):
        self.assertAlmostEqual(self.row[0], 500000.00, places=2)

    def test_y(self):
        self.assertAlmostEqual(self.row[1], 4000000.00, places=2)


class RiverBasinDistrictsSetupInitialRowMixin:
    def setUp(self):
        mommy.make(enhydris_models.GareaCategory, id=2, descr="River basins")
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO openhigis.RiverBasinDistricts
                (geographicalName, hydroId, remarks, geometry, objectId)
                VALUES
                ('Attica', '06', 'Hello world', 'SRID=2100;POINT(500000 4000000)', 1852)
                """
            )


class RiverBasinDistrictsInsertTestCase(
    EssentialTestsMixin, RiverBasinDistrictsSetupInitialRowMixin, TestCase
):
    model = models.RiverBasinDistrict
    view_name = "RiverBasinDistricts"
    expected_count = 1
    expected_name = "Attica"
    expected_code = "06"
    expected_remarks = "Hello world"
    expected_x = 24.00166
    expected_y = 36.14732


class RiverBasinDistrictsUpdateTestCase(
    EssentialTestsMixin, RiverBasinDistrictsSetupInitialRowMixin, TestCase
):
    model = models.RiverBasinDistrict
    view_name = "RiverBasinDistricts"
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
                UPDATE openhigis.RiverBasinDistricts
                SET geographicalName='Epirus', hydroId='08', remarks='Hello planet',
                geometry='SRID=2100;POINT(550000 4500000)'
                WHERE geographicalName='Attica'
                """
            )


class RiverBasinDistrictsDeleteTestCase(
    DeleteMixin, RiverBasinDistrictsSetupInitialRowMixin, TestCase
):
    model = models.RiverBasinDistrict
    view_name = "RiverBasinDistricts"


class RiverBasinDistrictsSridTestCase(
    SridMixin, RiverBasinDistrictsSetupInitialRowMixin, TestCase
):
    model = models.RiverBasinDistrict
    view_name = "RiverBasinDistricts"


class DrainageBasinsSetupInitialRowMixin:
    def setUp(self):
        mommy.make(enhydris_models.GareaCategory, id=2, descr="Drainage basins")
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO openhigis.{}
                (geographicalName, hydroId, remarks, geometry, origin, basinOrder,
                basinOrderScheme, basinOrderScope, totalArea, meanSlope, meanElevation,
                objectId)
                VALUES
                ('Attica', '06', 'Hello world', 'SRID=2100;POINT(500000 4000000)',
                'manMade', '18', 'strahler', 'go figure', 680, 0.15, 200, 1852)
                """.format(
                    self.view_name
                )
            )


class DrainageBasinsAdditionalTestsMixin:
    def test_man_made(self):
        self.assertEqual(self.model.objects.first().man_made, self.expected_man_made)

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

    def test_total_area(self):
        self.assertAlmostEqual(
            self.model.objects.first().total_area, self.expected_total_area
        )

    def test_mean_slope(self):
        self.assertAlmostEqual(
            self.model.objects.first().mean_slope, self.expected_mean_slope
        )

    def test_mean_elevation(self):
        self.assertAlmostEqual(
            self.model.objects.first().mean_elevation, self.expected_mean_elevation
        )


class DrainageBasinsInsertTestCase(
    EssentialTestsMixin,
    DrainageBasinsSetupInitialRowMixin,
    DrainageBasinsAdditionalTestsMixin,
    TestCase,
):
    model = models.DrainageBasin
    view_name = "DrainageBasins"
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


class DrainageBasinsUpdateTestCase(
    EssentialTestsMixin,
    DrainageBasinsSetupInitialRowMixin,
    DrainageBasinsAdditionalTestsMixin,
    TestCase,
):
    model = models.DrainageBasin
    view_name = "DrainageBasins"
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
                meanElevation=300
                WHERE geographicalName='Attica'
                """.format(
                    self.view_name
                )
            )


class DrainageBasinsDeleteTestCase(
    DeleteMixin, DrainageBasinsSetupInitialRowMixin, TestCase
):
    model = models.DrainageBasin
    view_name = "DrainageBasins"


class DrainageBasinsSridTestCase(
    SridMixin, DrainageBasinsSetupInitialRowMixin, TestCase
):
    model = models.DrainageBasin
    view_name = "DrainageBasins"


class RiverBasinsInsertTestCase(DrainageBasinsInsertTestCase):
    model = models.RiverBasin
    view_name = "RiverBasins"


class RiverBasinsUpdateTestCase(DrainageBasinsInsertTestCase):
    model = models.RiverBasin
    view_name = "RiverBasins"


class RiverBasinsDeleteTestCase(DrainageBasinsInsertTestCase):
    model = models.RiverBasin
    view_name = "RiverBasins"


class RiverBasinsSridTestCase(DrainageBasinsInsertTestCase):
    model = models.RiverBasin
    view_name = "RiverBasins"
