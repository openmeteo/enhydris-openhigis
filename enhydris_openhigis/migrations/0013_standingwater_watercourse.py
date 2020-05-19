from io import StringIO

import django.contrib.gis.db.models.fields
import django.db.models.deletion
from django.core.management import call_command
from django.db import IntegrityError, connection, migrations, models, transaction


def create_garea_categories(apps, schema_editor):
    @transaction.atomic
    def _create(id, descr):
        try:
            GareaCategory.objects.create(id=id, descr=descr)
        except IntegrityError:
            pass

    GareaCategory = apps.get_model("enhydris", "GareaCategory")
    _create(id=5, descr="Standing waters")

    # Reset the id sequence
    sqlsequencereset = StringIO()
    call_command("sqlsequencereset", "enhydris", "--no-color", stdout=sqlsequencereset)
    sqlsequencereset.seek(0)
    reset_sequence = [
        line for line in sqlsequencereset if '"enhydris_gareacategory"' in line
    ]
    assert len(reset_sequence) == 1
    with connection.cursor() as cursor:
        cursor.execute(reset_sequence[0])


def do_nothing(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("enhydris", "0025_gentity_geom"),
        ("enhydris_openhigis", "0012_limit_stations_to_openhi"),
    ]

    operations = [
        migrations.CreateModel(
            name="Watercourse",
            fields=[
                (
                    "gentity_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="enhydris.Gentity",
                    ),
                ),
                ("imported_id", models.IntegerField(unique=True)),
                (
                    "geom2100",
                    django.contrib.gis.db.models.fields.GeometryField(srid=2100),
                ),
                ("hydro_order", models.CharField(blank=True, max_length=50)),
                ("hydro_order_scheme", models.CharField(blank=True, max_length=50)),
                ("hydro_order_scope", models.CharField(blank=True, max_length=50)),
                ("local_type", models.CharField(max_length=50)),
                ("man_made", models.BooleanField(blank=True, null=True)),
                ("min_width", models.FloatField(blank=True, null=True)),
                ("max_width", models.FloatField(blank=True, null=True)),
                (
                    "river_basin",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="enhydris_openhigis.RiverBasin",
                    ),
                ),
            ],
            options={"abstract": False},
            bases=("enhydris.gentity", models.Model),
        ),
        migrations.CreateModel(
            name="StandingWater",
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
                ("imported_id", models.IntegerField(unique=True)),
                (
                    "geom2100",
                    django.contrib.gis.db.models.fields.GeometryField(srid=2100),
                ),
                ("local_type", models.CharField(max_length=50)),
                ("man_made", models.BooleanField(blank=True, null=True)),
                ("elevation", models.FloatField(blank=True, null=True)),
                ("mean_depth", models.FloatField(blank=True, null=True)),
                (
                    "river_basin",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="enhydris_openhigis.RiverBasin",
                    ),
                ),
            ],
            options={"abstract": False},
            bases=("enhydris.garea", models.Model),
        ),
        migrations.RunPython(create_garea_categories, do_nothing),
    ]
