import os

from django.db import connection, transaction
from django.db.models.signals import post_migrate
from django.dispatch import receiver


@receiver(post_migrate)
@transaction.atomic
def create_or_replace_views(sender, **kwargs):
    if (kwargs["app_config"].name != "enhydris_openhigis") or (not kwargs["plan"]):
        return
    create_views_pathname = os.path.join(os.path.dirname(__file__), "create_views.sql")
    with connection.cursor() as cursor:
        cursor.execute(open(create_views_pathname).read())
