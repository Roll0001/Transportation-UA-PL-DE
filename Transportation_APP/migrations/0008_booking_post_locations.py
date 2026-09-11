from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("Transportation_APP", "0007_bus_departure_time_bus_return_time"),
    ]

    operations = [
        migrations.AddField(
            model_name="booking",
            name="pickup_location",
            field=models.CharField(default="", max_length=255),
        ),
        migrations.AddField(
            model_name="booking",
            name="dropoff_location",
            field=models.CharField(default="", max_length=255),
        ),
        migrations.AddField(
            model_name="post",
            name="pickup_location",
            field=models.CharField(default="", max_length=255),
        ),
        migrations.AddField(
            model_name="post",
            name="dropoff_location",
            field=models.CharField(default="", max_length=255),
        ),
    ]