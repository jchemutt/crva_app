import csv
from django.core.management.base import BaseCommand
from WebApp.models import Province, Hazard, ProvinceTimeSeries
from hazard_layer.models import HazardLayer

class Command(BaseCommand):
    help = 'Import time-series data from transposed CSV (years as rows, provinces as columns)'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str)
        parser.add_argument('--name', required=True, help='Time series name')
        parser.add_argument('--hazard', required=True, help='Hazard name')
        parser.add_argument('--layer', help='HazardLayer name (optional)')

    def handle(self, *args, **options):
        name = options['name']
        hazard_name = options['hazard']
        layer_name = options.get('layer')

        # Get hazard
        try:
            hazard = Hazard.objects.get(name=hazard_name)
        except Hazard.DoesNotExist:
            self.stderr.write(self.style.ERROR(f"Hazard '{hazard_name}' not found."))
            return

        # Get optional layer
        layer = None
        if layer_name:
            try:
                layer = HazardLayer.objects.get(name=layer_name, hazard=hazard)
            except HazardLayer.DoesNotExist:
                self.stderr.write(self.style.ERROR(f"HazardLayer '{layer_name}' not found for hazard '{hazard_name}'."))
                return

        # Read and transpose CSV
        with open(options['csv_file'], newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                year_str = row.get("Year") or row.get("year")
                if not year_str:
                    continue
                try:
                    year = int(year_str)
                except ValueError:
                    continue

                for prov_name_raw, val in row.items():
                    if prov_name_raw.lower() in ["year"]:  # Skip 'Year' column
                        continue
                    prov_name = prov_name_raw.strip()  # Clean province name
                    if not val or val.strip() == "":
                        continue
                    try:
                        value = float(val)
                    except ValueError:
                        continue

                    # Create or get province
                    province, _ = Province.objects.get_or_create(name=prov_name)

                    # Save or update record
                    ProvinceTimeSeries.objects.update_or_create(
                        name=name,
                        province=province,
                        year=year,
                        hazard=hazard,
                        layer=layer,
                        defaults={'value': value},
                    )

        self.stdout.write(self.style.SUCCESS('Time-series import completed.'))
