from django.contrib.gis.geos import Point
from django.test import TestCase, override_settings
from django.urls import reverse

from model_mommy import mommy

from enhydris_openhigis import models
from enhydris_openhigis.views import get_all_geomodels


class GetAllGeomodelsTestCase(TestCase):
    def test_get_all_geomodels(self):
        self.assertEqual(
            get_all_geomodels(),
            {
                models.DrainageBasin,
                models.RiverBasin,
                models.RiverBasinDistrict,
                models.StandingWater,
                models.Station,
                models.StationBasin,
                models.Watercourse,
                models.HydroNode,
            },
        )


class SearchDataMixin:
    points = {
        "Northwest": (300, 4100),
        "Northeast hello": (500, 4000),
        "Southeast": (600, 3800),
        "Southwest hello": (400, 3900),
    }

    def setUp(self):
        super().setUp()
        for p in self.points:
            self._make_point(p, self.points[p])

    def _make_point(self, name, coordinates):
        mommy.make(
            models.Station,
            name=name,
            geom2100=Point(x=coordinates[0] * 1000, y=coordinates[1] * 1000, srid=2100),
            geom=Point(23, 38, srid=4326),
        )


class SearchViewTestCase(SearchDataMixin, TestCase):
    def _test(self, search_term, expected_x1, expected_y1, expected_x2, expected_y2):
        response = self.client.get(
            reverse("openhigis_search", kwargs={"search_term": search_term})
        )
        self.assertEqual(response.status_code, 200)
        x1, y1, x2, y2 = map(float, response.content.decode("utf-8").split())
        self.assertAlmostEqual(x1, expected_x1)
        self.assertAlmostEqual(y1, expected_y1)
        self.assertAlmostEqual(x2, expected_x2)
        self.assertAlmostEqual(y2, expected_y2)

    def test_search(self):
        self._test(
            search_term="hello",
            expected_x1=22.9025706,
            expected_y1=35.2407093,
            expected_x2=24.0016625,
            expected_y2=36.1473217,
        )

    @override_settings(ENHYDRIS_MAP_DEFAULT_VIEWPORT=[22, 35, 24, 36])
    def test_search_nonexistent(self):
        self._test(
            search_term="nonexistent",
            expected_x1=22.0,
            expected_y1=35.0,
            expected_x2=24.0,
            expected_y2=36.0,
        )
