from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Machine",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("deleted_at", models.DateTimeField(blank=True, default=None, null=True)),
                ("model", models.CharField(max_length=255)),
                ("serialnumber", models.CharField(max_length=255, unique=True)),
                ("owner_user", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="machines", to="accounts.user")),
            ],
        ),
        migrations.CreateModel(
            name="Production",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("deleted_at", models.DateTimeField(blank=True, default=None, null=True)),
                ("description", models.CharField(max_length=255)),
                ("quantity", models.PositiveIntegerField()),
                ("status", models.CharField(choices=[("STANDBY", "STANDBY"), ("ONGOING", "ONGOING"), ("FINISHED", "FINISHED"), ("CANCELED", "CANCELED")], default="STANDBY", max_length=32)),
                ("started_at", models.DateTimeField(blank=True, null=True)),
                ("finished_at", models.DateTimeField(blank=True, null=True)),
                ("canceled_at", models.DateTimeField(blank=True, null=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="productions", to="accounts.user")),
            ],
        ),
        migrations.CreateModel(
            name="ProductionMachine",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("deleted_at", models.DateTimeField(blank=True, default=None, null=True)),
                ("status", models.CharField(choices=[("STANDBY", "STANDBY"), ("ONGOING", "ONGOING"), ("HALT", "HALT"), ("FINISHED", "FINISHED"), ("CANCELED", "CANCELED")], default="STANDBY", max_length=32)),
                ("started_at", models.DateTimeField(blank=True, null=True)),
                ("finished_at", models.DateTimeField(blank=True, null=True)),
                ("canceled_at", models.DateTimeField(blank=True, null=True)),
                ("machine", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="machine_productions", to="core.machine")),
                ("production", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="production_machines", to="core.production")),
            ],
            options={},
        ),
        migrations.AddConstraint(
            model_name="productionmachine",
            constraint=models.UniqueConstraint(fields=("production", "machine"), name="uniq_production_machine_pair"),
        ),
    ]
