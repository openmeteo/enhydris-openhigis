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
    _create(id=2, descr="Water districts")
    _create(id=3, descr="River basins")
    _create(id=4, descr="Drainage basins")


def do_nothing(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [("enhydris_openhigis", "0008_imported_id_part_b")]

    operations = [
        migrations.DeleteModel("RiverBasin"),
        migrations.DeleteModel("DrainageBasin"),
        migrations.CreateModel(
            name="RiverBasin",
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
                ("hydro_order", models.CharField(blank=True, max_length=50)),
                ("hydro_order_scheme", models.CharField(blank=True, max_length=50)),
                ("hydro_order_scope", models.CharField(blank=True, max_length=50)),
                ("man_made", models.BooleanField(blank=True, null=True)),
                ("total_area", models.FloatField(blank=True, null=True)),
                ("mean_slope", models.FloatField(blank=True, null=True)),
                ("mean_elevation", models.FloatField(blank=True, null=True)),
            ],
            options={"abstract": False},
            bases=("enhydris.garea", models.Model),
        ),
        migrations.CreateModel(
            name="DrainageBasin",
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
                ("hydro_order", models.CharField(blank=True, max_length=50)),
                ("hydro_order_scheme", models.CharField(blank=True, max_length=50)),
                ("hydro_order_scope", models.CharField(blank=True, max_length=50)),
                ("man_made", models.BooleanField(blank=True, null=True)),
                ("total_area", models.FloatField(blank=True, null=True)),
                ("mean_slope", models.FloatField(blank=True, null=True)),
                ("mean_elevation", models.FloatField(blank=True, null=True)),
                (
                    "river_basin",
                    models.ForeignKey(
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
