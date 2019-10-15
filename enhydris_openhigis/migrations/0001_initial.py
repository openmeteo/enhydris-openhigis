import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [("enhydris", "0025_gentity_geom")]

    operations = [
        migrations.CreateModel(
            name="WaterDistrict",
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
                ("length", models.FloatField(default=0)),
                ("area", models.FloatField(default=0)),
            ],
            bases=("enhydris.garea",),
        )
    ]
