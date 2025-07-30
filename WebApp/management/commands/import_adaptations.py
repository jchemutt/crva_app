import csv
from django.core.management.base import BaseCommand
from WebApp.models import Province, ValueChain, Hazard, Stage, ValueChainHazard, RiskAdaptation

def clean_text(value):
    return value.strip().strip('"').strip("'")
class Command(BaseCommand):
    help = 'Import adaptation data from a structured CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file')

  

    def handle(self, *args, **options):
        csv_file_path = options['csv_file']
        created_count = 0
        skipped = 0

        try:
            with open(csv_file_path, newline='', encoding='ISO-8859-1') as csvfile:
                reader = csv.DictReader(csvfile)

                for row in reader:
                    try:
                        province_name = clean_text(row['Province'])
                        vc_name = clean_text(row['Value Chain'])
                        hazard_name = clean_text(row['Hazard'])
                        stage_name = clean_text(row['Stage'])
                        risk = clean_text(row['Risk'])
                        strategy = clean_text(row.get('Adaptation Strategy', ''))

                        # Skip rows with missing required fields
                        if not all([province_name, vc_name, hazard_name, stage_name]):
                            skipped += 1
                            continue

                        province, _ = Province.objects.get_or_create(name=province_name)
                        vc, _ = ValueChain.objects.get_or_create(name=vc_name)
                        hazard, _ = Hazard.objects.get_or_create(name=hazard_name)
                        stage, _ = Stage.objects.get_or_create(name=stage_name)
                        vc_hazard, _ = ValueChainHazard.objects.get_or_create(value_chain=vc, hazard=hazard)

                        RiskAdaptation.objects.create(
                            vc_hazard=vc_hazard,
                            stage=stage,
                            province=province,
                            risk=risk,
                            adaptation_strategy=strategy
                        )
                        created_count += 1

                    except Exception as e:
                        self.stderr.write(self.style.ERROR(f"Skipped row due to error: {e}"))

            self.stdout.write(self.style.SUCCESS(f"Successfully imported {created_count} records."))
            if skipped:
                self.stdout.write(self.style.WARNING(f"Skipped {skipped} incomplete or invalid rows."))

        except FileNotFoundError:
            self.stderr.write(self.style.ERROR("File not found. Please provide a valid CSV path."))
