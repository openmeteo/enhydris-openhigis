import os

import django.db.models.deletion
from django.db import migrations, models

create_views_pathname = os.path.join(os.path.dirname(__file__), "create_views.sql")


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
                ("perimeter_length", models.FloatField()),
                ("area", models.FloatField()),
            ],
            bases=("enhydris.garea",),
        ),
        migrations.RunSQL(open(create_views_pathname).read()),
    ]
