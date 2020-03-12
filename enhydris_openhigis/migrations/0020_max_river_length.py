# Generated by Django 2.2.7 on 2020-03-12 16:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("enhydris_openhigis", "0019_fix_foreignkey_stationbasin_river_basin"),
    ]

    operations = [
        migrations.AddField(
            model_name="basin",
            name="max_river_length",
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="stationbasin",
            name="max_river_length",
            field=models.FloatField(blank=True, null=True),
        ),
    ]
