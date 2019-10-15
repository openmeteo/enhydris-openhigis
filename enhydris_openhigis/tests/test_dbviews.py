from django.db import connection
from django.test import TestCase

from model_mommy import mommy

from enhydris import models as enhydris_models
from enhydris_openhigis import models


class RiverBasinDistrictsDataMixin:
    def setUp(self):
        mommy.make(enhydris_models.GareaCategory, id=2, descr="River basin district")
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO openhigis.river_basin_districts
                (name, code, remarks, geom)
                VALUES
                ('Attica', '06', 'Hello world', 'SRID=4326;POINT(23 38)')
                """
            )


class RiverBasinDistrictsInsertTestCase(RiverBasinDistrictsDataMixin, TestCase):
    expected_count = 1
    expected_name = "Attica"
    expected_code = "06"
    expected_remarks = "Hello world"
    expected_x = 23.0
    expected_y = 38.0

    def test_rowcount(self):
        self.assertEqual(models.RiverBasinDistrict.objects.count(), self.expected_count)

    def test_name(self):
        self.assertEqual(
            models.RiverBasinDistrict.objects.first().name, self.expected_name
        )

    def test_code(self):
        self.assertEqual(
            models.RiverBasinDistrict.objects.first().code, self.expected_code
        )

    def test_remarks(self):
        self.assertEqual(
            models.RiverBasinDistrict.objects.first().remarks, self.expected_remarks
        )

    def test_geom_x(self):
        self.assertAlmostEqual(
            models.RiverBasinDistrict.objects.first().geom.x, self.expected_x
        )

    def test_geom_y(self):
        self.assertAlmostEqual(
            models.RiverBasinDistrict.objects.first().geom.y, self.expected_y
        )


class RiverBasinDistrictsUpdateTestCase(RiverBasinDistrictsInsertTestCase):
    expected_count = 1
    expected_name = "Epirus"
    expected_code = "08"
    expected_remarks = "Hello planet"
    expected_x = 24.0
    expected_y = 39.0

    def setUp(self):
        super().setUp()
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE openhigis.river_basin_districts
                SET name='Epirus', code='08', remarks='Hello planet',
                geom='SRID=4326;POINT(24 39)'
                WHERE name='Attica'
                """
            )


class RiverBasinDistrictsDeleteTestCase(RiverBasinDistrictsDataMixin, TestCase):
    def setUp(self):
        super().setUp()
        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM openhigis.river_basin_districts WHERE name='Attica'"
            )

    def test_count(self):
        self.assertEqual(models.RiverBasinDistrict.objects.count(), 0)


class RiverBasinDistrictsSridTestCase(RiverBasinDistrictsDataMixin, TestCase):
    def setUp(self):
        super().setUp()
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT ST_X(geom), ST_Y(geom)
                FROM openhigis.river_basin_districts WHERE name='Attica'
                """
            )
            self.row = cursor.fetchone()

    def test_x(self):
        self.assertAlmostEqual(self.row[0], 412051.58, places=2)

    def test_y(self):
        self.assertAlmostEqual(self.row[1], 4205998.82, places=2)
