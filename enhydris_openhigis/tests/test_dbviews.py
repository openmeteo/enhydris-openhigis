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
                INSERT INTO openhigis.RiverBasinDistricts
                (geographicalName, hydroId, remarks, geometry)
                VALUES
                ('Attica', '06', 'Hello world', 'SRID=2100;POINT(500000 4000000)')
                """
            )


class RiverBasinDistrictsInsertTestCase(RiverBasinDistrictsDataMixin, TestCase):
    expected_count = 1
    expected_name = "Attica"
    expected_code = "06"
    expected_remarks = "Hello world"
    expected_x = 24.00166
    expected_y = 36.14732

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
            models.RiverBasinDistrict.objects.first().geom.x, self.expected_x, places=5
        )

    def test_geom_y(self):
        self.assertAlmostEqual(
            models.RiverBasinDistrict.objects.first().geom.y, self.expected_y, places=5
        )


class RiverBasinDistrictsUpdateTestCase(RiverBasinDistrictsInsertTestCase):
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


class RiverBasinDistrictsDeleteTestCase(RiverBasinDistrictsDataMixin, TestCase):
    def setUp(self):
        super().setUp()
        with connection.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM openhigis.RiverBasinDistricts
                WHERE geographicalName='Attica'
                """
            )

    def test_count(self):
        self.assertEqual(models.RiverBasinDistrict.objects.count(), 0)


class RiverBasinDistrictsSridTestCase(RiverBasinDistrictsDataMixin, TestCase):
    def setUp(self):
        super().setUp()
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT ST_X(geometry), ST_Y(geometry)
                FROM openhigis.RiverBasinDistricts WHERE geographicalName='Attica'
                """
            )
            self.row = cursor.fetchone()

    def test_x(self):
        self.assertAlmostEqual(self.row[0], 500000.00, places=2)

    def test_y(self):
        self.assertAlmostEqual(self.row[1], 4000000.00, places=2)
