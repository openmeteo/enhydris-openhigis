import django.contrib.gis.db.models.fields
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("enhydris", "0025_gentity_geom"),
        ("enhydris_openhigis", "0014_basin_multitable_inheritance"),
    ]

    operations = [
        migrations.CreateModel(
            name="SurfaceWater",
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
                ("local_type", models.CharField(max_length=50)),
                ("man_made", models.BooleanField(blank=True, null=True)),
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
        migrations.AddField(
            model_name="standingwater",
            name="surfacewater_ptr",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                to="enhydris_openhigis.SurfaceWater",
                blank=True,
                null=True,
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="watercourse",
            name="surfacewater_ptr",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                to="enhydris_openhigis.SurfaceWater",
                blank=True,
                null=True,
            ),
            preserve_default=False,
        ),
        migrations.RunSQL(
            """
            INSERT INTO enhydris_openhigis_surfacewater
            (gentity_ptr_id, geom2100, imported_id, local_type, man_made,
            river_basin_id)
            SELECT gentity_ptr_id, geom2100, imported_id, local_type, man_made,
            river_basin_id
            FROM enhydris_openhigis_watercourse;
            """
        ),
        migrations.RunSQL(
            """
            INSERT INTO enhydris_openhigis_surfacewater
            (gentity_ptr_id, geom2100, imported_id, local_type, man_made,
            river_basin_id)
            SELECT garea_ptr_id, geom2100, imported_id, local_type, man_made,
            river_basin_id
            FROM enhydris_openhigis_standingwater;
            """
        ),
        migrations.RunSQL(
            """
            UPDATE enhydris_openhigis_watercourse
            SET surfacewater_ptr_id=gentity_ptr_id;
            """
        ),
        migrations.RunSQL(
            """
            UPDATE enhydris_openhigis_standingwater
            SET surfacewater_ptr_id=garea_ptr_id;
            """
        ),
        migrations.RemoveField(model_name="watercourse", name="gentity_ptr"),
        migrations.RemoveField(model_name="standingwater", name="garea_ptr"),
        migrations.RunSQL(
            """
            DELETE FROM enhydris_garea WHERE gentity_ptr_id IN
                (SELECT gentity_ptr_id FROM enhydris_openhigis_surfacewater);
            """
        ),
        migrations.AlterField(
            model_name="standingwater",
            name="surfacewater_ptr",
            field=models.OneToOneField(
                auto_created=True,
                on_delete=django.db.models.deletion.CASCADE,
                parent_link=True,
                primary_key=True,
                serialize=False,
                to="enhydris_openhigis.SurfaceWater",
            ),
        ),
        migrations.AlterField(
            model_name="watercourse",
            name="surfacewater_ptr",
            field=models.OneToOneField(
                auto_created=True,
                on_delete=django.db.models.deletion.CASCADE,
                parent_link=True,
                primary_key=True,
                serialize=False,
                to="enhydris_openhigis.SurfaceWater",
            ),
        ),
        migrations.RemoveField(model_name="standingwater", name="geom2100"),
        migrations.RemoveField(model_name="standingwater", name="imported_id"),
        migrations.RemoveField(model_name="standingwater", name="local_type"),
        migrations.RemoveField(model_name="standingwater", name="man_made"),
        migrations.RemoveField(model_name="standingwater", name="river_basin"),
        migrations.RemoveField(model_name="watercourse", name="geom2100"),
        migrations.RemoveField(model_name="watercourse", name="imported_id"),
        migrations.RemoveField(model_name="watercourse", name="local_type"),
        migrations.RemoveField(model_name="watercourse", name="man_made"),
        migrations.RemoveField(model_name="watercourse", name="river_basin"),
    ]
