import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("enhydris_openhigis", "0015_surface_water_multitable_inheritance"),
    ]

    operations = [
        migrations.AddField(
            model_name="station",
            name="basin",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="enhydris_openhigis.Basin",
            ),
        ),
        migrations.AddField(
            model_name="station",
            name="surface_water",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="enhydris_openhigis.SurfaceWater",
            ),
        ),
    ]
