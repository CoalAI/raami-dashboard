from django.contrib.auth.models import User
from django.db import migrations
from django.db.backends.sqlite3.schema import DatabaseSchemaEditor
from django.db.migrations.state import StateApps


def createsuperuser(apps: StateApps, schema_editor: DatabaseSchemaEditor) -> None:
    """
    Dynamically create an admin user as part of a migration
    """
    User.objects.create_superuser("admin", password="admin".strip())


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]
    operations = [migrations.RunPython(createsuperuser)]
