from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("enhydris", "0025_gentity_geom"),
        ("enhydris_openhigis", "0011_stationbasin"),
    ]

    operations = [
        migrations.RunSQL(
            "DELETE FROM enhydris_openhigis_station WHERE station_ptr_id NOT IN ("
            "1344, 1354, 1358, 1360, 1458, 1461, 1462, 1463, 1464, 1466, 1481, 1482, "
            "1484, 1485, 1534);",
            reverse_sql="",
        )
    ]
