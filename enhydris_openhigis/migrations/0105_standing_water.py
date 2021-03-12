# Generated by Django 2.2.19 on 2021-03-12 11:01

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("enhydris_openhigis", "0104_delete_max_river_length"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="watercourse",
            name="outlet",
        ),
        migrations.AddField(
            model_name="standingwater",
            name="surface_area",
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="surfacewater",
            name="outlet",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="enhydris_openhigis.HydroNode",
            ),
        ),
    ]
