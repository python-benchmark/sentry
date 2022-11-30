# Generated by Django 2.2.28 on 2022-08-15 23:06

from django.db import migrations

import sentry.db.models.fields.bounded
from sentry.new_migrations.migrations import CheckedMigration


class Migration(CheckedMigration):
    # This flag is used to mark that a migration shouldn't be automatically run in production. For
    # the most part, this should only be used for operations where it's safe to run the migration
    # after your code has deployed. So this should not be used for most operations that alter the
    # schema of a table.
    # Here are some things that make sense to mark as dangerous:
    # - Large data migrations. Typically we want these to be run manually by ops so that they can
    #   be monitored and not block the deploy for a long period of time while they run.
    # - Adding indexes to large tables. Since this can take a long time, we'd generally prefer to
    #   have ops run this and not block the deploy. Note that while adding an index is a schema
    #   change, it's completely safe to run the operation after the code has deployed.
    is_dangerous = True

    # This flag is used to decide whether to run this migration in a transaction or not. Generally
    # we don't want to run in a transaction here, since for long running operations like data
    # back-fills this results in us locking an increasing number of rows until we finally commit.
    atomic = False

    dependencies = [
        ("sentry", "0314_bit_int_for_org_and_project_id"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    """
                    ALTER TABLE "sentry_groupedmessage" ADD COLUMN "type" integer NOT NULL DEFAULT 1;
                    """,
                    reverse_sql="""
                    ALTER TABLE "sentry_groupedmessage" DROP COLUMN "type";
                    """,
                    hints={"tables": ["sentry_groupedmessage"]},
                ),
            ],
            state_operations=[
                migrations.AddField(
                    model_name="group",
                    name="type",
                    field=sentry.db.models.fields.bounded.BoundedPositiveIntegerField(default=1),
                ),
            ],
        )
    ]
