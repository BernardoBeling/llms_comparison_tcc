from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="productionmachine",
            name="working_time",
            field=models.PositiveIntegerField(default=0),
        ),
    ]
