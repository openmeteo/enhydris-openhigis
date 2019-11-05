from django.db import migrations, models


def set_imported_id(apps, schema_editor):
    DrainageBasin = apps.get_model("enhydris_openhigis", "DrainageBasin")
    RiverBasinDistrict = apps.get_model("enhydris_openhigis", "RiverBasinDistrict")
    for obj in DrainageBasin.objects.all():
        obj.imported_id = obj.id
        obj.save()
    for obj in RiverBasinDistrict.objects.all():
        obj.imported_id = obj.id
        obj.save()


def do_nothing(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [("enhydris_openhigis", "0006_drainagebasin")]

    operations = [
        migrations.AddField(
            model_name="drainagebasin",
            name="imported_id",
            field=models.IntegerField(default=-1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="riverbasindistrict",
            name="imported_id",
            field=models.IntegerField(default=-1),
            preserve_default=False,
        ),
        migrations.RunPython(set_imported_id, reverse_code=do_nothing),
    ]
