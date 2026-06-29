# Correction FK django_admin_log.user_id → core_user (BDD partagée register/RH)

from django.db import migrations


def _admin_log_user_fk_target(cursor):
    cursor.execute(
        """
        SELECT ccu.table_name AS foreign_table
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
          ON tc.constraint_name = kcu.constraint_name
          AND tc.table_schema = kcu.table_schema
        JOIN information_schema.constraint_column_usage ccu
          ON ccu.constraint_name = tc.constraint_name
          AND ccu.table_schema = tc.table_schema
        WHERE tc.constraint_type = 'FOREIGN KEY'
          AND tc.table_name = 'django_admin_log'
          AND kcu.column_name = 'user_id'
        LIMIT 1
        """
    )
    row = cursor.fetchone()
    return row[0] if row else None


def forwards(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return

    with schema_editor.connection.cursor() as cursor:
        if _admin_log_user_fk_target(cursor) != "auth_user":
            return

        cursor.execute(
            "ALTER TABLE django_admin_log "
            "DROP CONSTRAINT IF EXISTS django_admin_log_user_id_c564eba6_fk_auth_user_id"
        )
        cursor.execute(
            """
            ALTER TABLE django_admin_log
            ADD CONSTRAINT django_admin_log_user_id_fk_core_user
            FOREIGN KEY (user_id) REFERENCES core_user(id)
            DEFERRABLE INITIALLY DEFERRED
            """
        )


def backwards(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return

    with schema_editor.connection.cursor() as cursor:
        if _admin_log_user_fk_target(cursor) != "core_user":
            return

        cursor.execute(
            "ALTER TABLE django_admin_log "
            "DROP CONSTRAINT IF EXISTS django_admin_log_user_id_fk_core_user"
        )
        cursor.execute(
            """
            ALTER TABLE django_admin_log
            ADD CONSTRAINT django_admin_log_user_id_c564eba6_fk_auth_user_id
            FOREIGN KEY (user_id) REFERENCES auth_user(id)
            DEFERRABLE INITIALLY DEFERRED
            """
        )


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0003_alter_user_managers_alter_importer_status"),
        ("admin", "0003_logentry_add_action_flag_choices"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
