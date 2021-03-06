# Generated by Django 2.2.7 on 2019-11-07 12:50

import django.contrib.gis.db.models.fields
import django.db.models.deletion
from django.db import IntegrityError, migrations, models, transaction


def create_garea_categories(apps, schema_editor):
    @transaction.atomic
    def _create(id, descr):
        try:
            GareaCategory.objects.create(id=id, descr=descr)
        except IntegrityError:
            pass

    GareaCategory = apps.get_model("enhydris", "GareaCategory")
    _create(id=5, descr="Station basins")


def do_nothing(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("enhydris", "0025_gentity_geom"),
        ("enhydris_openhigis", "0010_remove_useless_fields_from_riverbasin"),
    ]

    operations = [
        migrations.CreateModel(
            name="StationBasin",
            fields=[
                (
                    "garea_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="enhydris.Garea",
                    ),
                ),
                (
                    "geom2100",
                    django.contrib.gis.db.models.fields.GeometryField(srid=2100),
                ),
                ("man_made", models.BooleanField(blank=True, null=True)),
                ("mean_slope", models.FloatField(blank=True, null=True)),
                ("mean_elevation", models.FloatField(blank=True, null=True)),
                (
                    "river_basin",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="enhydris_openhigis.RiverBasin",
                    ),
                ),
                (
                    "station",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="enhydris_openhigis.Station",
                    ),
                ),
            ],
            options={"abstract": False},
            bases=("enhydris.garea", models.Model),
        ),
        migrations.RunPython(create_garea_categories, do_nothing),
    ]
