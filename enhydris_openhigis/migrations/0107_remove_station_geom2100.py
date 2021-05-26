from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("enhydris_openhigis", "0106_hydro_node_category"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="station",
            name="geom2100",
        ),
    ]
