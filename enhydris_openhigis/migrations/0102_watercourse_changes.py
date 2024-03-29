# Generated by Django 2.2.17 on 2021-02-23 16:21

import django.contrib.gis.db.models.fields
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("enhydris", "0108_gentity_images_data"),
        ("enhydris_openhigis", "0101_squashed"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="watercourse",
            name="end_node",
        ),
        migrations.RemoveField(
            model_name="watercourse",
            name="max_width",
        ),
        migrations.RemoveField(
            model_name="watercourse",
            name="min_width",
        ),
        migrations.RemoveField(
            model_name="watercourse",
            name="start_node",
        ),
        migrations.AddField(
            model_name="surfacewater",
            name="level_of_detail",
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="watercourse",
            name="delineation_known",
            field=models.BooleanField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="watercourse",
            name="length",
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="watercourse",
            name="level",
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="watercourse",
            name="width",
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="watercourse",
            name="slope",
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="watercourse",
            name="outlet",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="enhydris_openhigis.HydroNode",
                blank=True,
                null=True,
            ),
        ),
        migrations.CreateModel(
            name="WatercourseLink",
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
                ("length", models.FloatField(blank=True, null=True)),
                (
                    "flow_direction",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("inDirection", "in direction"),
                            ("bothDirections", "both directions"),
                            ("inOppositeDirection", "in opposite direction"),
                        ],
                        max_length=19,
                    ),
                ),
                (
                    "end_node",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="watercourselinks_ending",
                        to="enhydris_openhigis.HydroNode",
                    ),
                ),
                (
                    "start_node",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="watercourselinks_starting",
                        to="enhydris_openhigis.HydroNode",
                    ),
                ),
                ("fictitious", models.BooleanField()),
            ],
            options={
                "abstract": False,
            },
            bases=("enhydris.gentity", models.Model),
        ),
    ]
