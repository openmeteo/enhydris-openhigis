from django.db import connection
from django.test import TestCase

from model_mommy import mommy

from enhydris import models as enhydris_models
from enhydris_openhigis import models


class DbviewDataMixin:
    def setUp(self):
        mommy.make(enhydris_models.GareaCategory, id=2, descr="River basin district")
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO openhigis.{}
                (geographicalName, hydroId, remarks, geometry)
                VALUES
                ('Attica', '06', 'Hello world', 'SRID=2100;POINT(500000 4000000)')
                """.format(
                    self.view_name
                )
            )


class DbviewInsertTestCaseBase(DbviewDataMixin):
    expected_count = 1
    expected_name = "Attica"
    expected_code = "06"
    expected_remarks = "Hello world"
    expected_x = 24.00166
    expected_y = 36.14732

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


class DbviewUpdateTestCaseBase(DbviewInsertTestCaseBase):
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
                UPDATE openhigis.{}
                SET geographicalName='Epirus', hydroId='08', remarks='Hello planet',
                geometry='SRID=2100;POINT(550000 4500000)'
                WHERE geographicalName='Attica'
                """.format(
                    self.view_name
                )
            )


class DbviewDeleteTestCaseBase(DbviewDataMixin):
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


class DbviewSridTestCaseBase(DbviewDataMixin):
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


dbviews = [
    {"view_name": "RiverBasinDistricts", "model": models.RiverBasinDistrict},
    {"view_name": "RiverBasins", "model": models.RiverBasin},
]


def create_dynamic_test_case(dbview, base_class):
    testcasename = "{}{}".format(dbview["view_name"], base_class.__name__)
    testcase = type(testcasename, (base_class, TestCase), dbview)
    globals()[testcasename] = testcase


for dbview in dbviews:
    create_dynamic_test_case(dbview, DbviewInsertTestCaseBase)
    create_dynamic_test_case(dbview, DbviewUpdateTestCaseBase)
    create_dynamic_test_case(dbview, DbviewDeleteTestCaseBase)
    create_dynamic_test_case(dbview, DbviewSridTestCaseBase)
