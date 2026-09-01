from django.db import migrations
from django.utils import timezone


def seed_buses(apps, schema_editor):
    """Create default independent outbound/return bus records."""
    from Transportation_APP.forms import get_bus_direction_dates
    
    Bus = apps.get_model('Transportation_APP', 'Bus')
    
    for bus_number in [1, 2]:
        outbound_departure, outbound_return = get_bus_direction_dates(bus_number, is_return_trip=False)
        return_departure, return_return = get_bus_direction_dates(bus_number, is_return_trip=True)
        
        Bus.objects.get_or_create(
            number=bus_number,
            direction="outbound",
            defaults={
                "departure_date": outbound_departure,
                "return_date": outbound_return,
                "note": "Автобус у напрямку до польського маршруту.",
            },
        )
        
        Bus.objects.get_or_create(
            number=bus_number,
            direction="return",
            defaults={
                "departure_date": return_departure,
                "return_date": return_return,
                "note": "Автобус повернення назад.",
            },
        )


def reverse_seed(apps, schema_editor):
    """Remove seeded bus records if migration is reversed."""
    Bus = apps.get_model('Transportation_APP', 'Bus')
    Bus.objects.filter(direction__in=['outbound', 'return']).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('Transportation_APP', '0005_alter_bus_options_remove_bus_group_bus_direction_and_more'),
    ]

    operations = [
        migrations.RunPython(seed_buses, reverse_seed),
    ]
