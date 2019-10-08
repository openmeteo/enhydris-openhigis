from django.db import models

from enhydris.models import Garea


class WaterDistrict(Garea):
    length = models.FloatField()
    area = models.FloatField()
