from django.db import migrations

def seed_components(apps, schema_editor):
    Component = apps.get_model("WebApp", "Component")
    Hazard = apps.get_model("WebApp", "Hazard")

    # Create canonical components
    comps = {
        "hazard": "Hazard",
        "exposure": "Exposure",
        "sensitivity": "Sensitivity",
        "adaptive_capacity": "Adaptive Capacity",
    }
    for key, label in comps.items():
        Component.objects.get_or_create(key=key, defaults={"label": label})

    # Assign existing hazards to 'hazard' by default
    haz_comp = Component.objects.get(key="hazard")
    Hazard.objects.filter(component__isnull=True).update(component=haz_comp)

def unseed_components(apps, schema_editor):
    # usually leave as no-op to avoid deleting referenced rows
    pass

class Migration(migrations.Migration):

    dependencies = [
         ('WebApp', '0009_component_alter_hazard_options_alter_hazard_name_and_more'),
    ]

    operations = [
        migrations.RunPython(seed_components, reverse_code=unseed_components),
    ]
