import os
from django.core.management.base import BaseCommand
from django.contrib.gis.utils import LayerMapping
from django.conf import settings
from WebApp.models import Province

class Command(BaseCommand):
    help = "Load province boundaries from a shapefile"

    def handle(self, *args, **options):
        shapefile_path = os.path.join(settings.BASE_DIR, 'data', 'shapefiles', 'gadm41_MOZ_1.shp')

        mapping = {
            'name': 'NAME_1', 
            'boundary': 'MULTIPOLYGON',
        }

        lm = LayerMapping(Province, shapefile_path, mapping, transform=True)
        lm.save(strict=True, verbose=True)

        self.stdout.write(self.style.SUCCESS("Province boundaries imported successfully."))
