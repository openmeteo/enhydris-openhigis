import django.contrib.gis.db.models.fields
import django.db.models.deletion
from django.db import migrations, models


def populate_basin_ptr(apps, schema_editor):
    DrainageBasin = apps.get_model("enhydris_openhigis", "DrainageBasin")
    RiverBasin = apps.get_model("enhydris_openhigis", "RiverBasin")
    for basin in DrainageBasin.objects.all():
        basin.basin_ptr_id = basin.garea_ptr_id
        basin.save()
    for basin in RiverBasin.objects.all():
        basin.basin_ptr_id = basin.garea_ptr_id
        basin.save()


class Migration(migrations.Migration):

    dependencies = [
        ("enhydris", "0025_gentity_geom"),
        ("enhydris_openhigis", "0013_standingwater_watercourse"),
    ]

    operations = [
        migrations.CreateModel(
            name="Basin",
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
                ("man_made", models.BooleanField(blank=True, null=True)),
                ("mean_slope", models.FloatField(blank=True, null=True)),
                ("mean_elevation", models.FloatField(blank=True, null=True)),
            ],
            options={"abstract": False},
            bases=("enhydris.garea", models.Model),
        ),
        migrations.RunSQL(
            """
            INSERT INTO enhydris_openhigis_basin
            (garea_ptr_id, imported_id, geom2100, man_made, mean_slope, mean_elevation)
            SELECT garea_ptr_id, imported_id, geom2100, man_made, mean_slope,
            mean_elevation
            FROM enhydris_openhigis_riverbasin;
            """
        ),
        migrations.RunSQL(
            """
            INSERT INTO enhydris_openhigis_basin
            (garea_ptr_id, imported_id, geom2100, man_made, mean_slope, mean_elevation)
            SELECT garea_ptr_id, imported_id, geom2100, man_made, mean_slope,
            mean_elevation
            FROM enhydris_openhigis_drainagebasin;
            """
        ),
        migrations.AddField(
            model_name="drainagebasin",
            name="basin_ptr",
            field=models.OneToOneField(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="enhydris_openhigis.Basin",
            ),
        ),
        migrations.AddField(
            model_name="riverbasin",
            name="basin_ptr",
            field=models.OneToOneField(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="enhydris_openhigis.Basin",
            ),
        ),
        migrations.RunPython(populate_basin_ptr),
        migrations.RemoveField(model_name="drainagebasin", name="garea_ptr"),
        migrations.RemoveField(model_name="drainagebasin", name="geom2100"),
        migrations.RemoveField(model_name="drainagebasin", name="imported_id"),
        migrations.RemoveField(model_name="drainagebasin", name="man_made"),
        migrations.RemoveField(model_name="drainagebasin", name="mean_elevation"),
        migrations.RemoveField(model_name="drainagebasin", name="mean_slope"),
        migrations.RemoveField(model_name="riverbasin", name="garea_ptr"),
        migrations.RemoveField(model_name="riverbasin", name="geom2100"),
        migrations.RemoveField(model_name="riverbasin", name="imported_id"),
        migrations.RemoveField(model_name="riverbasin", name="man_made"),
        migrations.RemoveField(model_name="riverbasin", name="mean_elevation"),
        migrations.RemoveField(model_name="riverbasin", name="mean_slope"),
        migrations.AlterField(
            model_name="drainagebasin",
            name="basin_ptr",
            field=models.OneToOneField(
                auto_created=True,
                on_delete=django.db.models.deletion.CASCADE,
                parent_link=True,
                primary_key=True,
                serialize=False,
                to="enhydris_openhigis.Basin",
            ),
        ),
        migrations.AlterField(
            model_name="riverbasin",
            name="basin_ptr",
            field=models.OneToOneField(
                auto_created=True,
                on_delete=django.db.models.deletion.CASCADE,
                parent_link=True,
                primary_key=True,
                serialize=False,
                to="enhydris_openhigis.Basin",
            ),
        ),
    ]
