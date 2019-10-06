from django.db import models

from enhydris.models import Garea


class WaterDistrict(Garea):
    perimeter_length = models.FloatField()
    area = models.FloatField()
