import django.contrib.gis.db.models.fields
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("enhydris", "0025_gentity_geom"),
        ("enhydris_openhigis", "0016_add_fields_to_station"),
    ]

    operations = [
        migrations.CreateModel(
            name="HydroNode",
            fields=[
                (
                    "gpoint_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="enhydris.Gpoint",
                    ),
                ),
                ("imported_id", models.IntegerField(unique=True)),
                (
                    "geom2100",
                    django.contrib.gis.db.models.fields.GeometryField(srid=2100),
                ),
            ],
            options={"abstract": False},
            bases=("enhydris.gpoint", models.Model),
        ),
        migrations.AddField(
            model_name="watercourse",
            name="end_node",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="watercourses_ending",
                to="enhydris_openhigis.HydroNode",
            ),
        ),
        migrations.AddField(
            model_name="watercourse",
            name="start_node",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="watercourses_starting",
                to="enhydris_openhigis.HydroNode",
            ),
        ),
    ]
