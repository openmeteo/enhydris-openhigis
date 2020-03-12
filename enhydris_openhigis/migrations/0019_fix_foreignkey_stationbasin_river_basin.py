from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("enhydris_openhigis", "0018_stationbasin_unique_station"),
    ]

    # We are manually adding the constraint below because it has been deleted
    # earlier by a Django bug (https://code.djangoproject.com/ticket/31343)

    operations = [
        migrations.RunSQL(
            """
            ALTER TABLE enhydris_openhigis_stationbasin
                ADD CONSTRAINT enhydris_openhigis_stationbasin_river_basin_id
                FOREIGN KEY (river_basin_id)
                REFERENCES enhydris_openhigis_riverbasin(basin_ptr_id);
            """
        )
    ]
