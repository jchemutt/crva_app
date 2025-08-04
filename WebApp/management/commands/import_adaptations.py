import csv
from django.core.management.base import BaseCommand
from WebApp.models import (
    Province, ValueChain, Hazard, Stage,
    ValueChainHazard, Risk, AdaptationStrategy, RiskAdaptation
)

def clean_text(value):
    return value.strip().strip('"').strip("'") if value else ""

class Command(BaseCommand):
    help = 'Import adaptation strategies and risks from structured CSV file'

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
                        risk_text = clean_text(row['Risk'])
                        strategy_text = clean_text(row.get('Adaptation Strategy', ''))

                        # Ensure required fields are present
                        if not all([province_name, vc_name, hazard_name, stage_name, risk_text]):
                            skipped += 1
                            continue

                        # Get or create all related objects
                        province, _ = Province.objects.get_or_create(name=province_name)
                        vc, _ = ValueChain.objects.get_or_create(name=vc_name)
                        hazard, _ = Hazard.objects.get_or_create(name=hazard_name)
                        stage, _ = Stage.objects.get_or_create(name=stage_name)
                        vc_hazard, _ = ValueChainHazard.objects.get_or_create(value_chain=vc, hazard=hazard)

                        risk, _ = Risk.objects.get_or_create(description=risk_text)
                        strategy, _ = AdaptationStrategy.objects.get_or_create(description=strategy_text)

                        # Create the RiskAdaptation record
                        RiskAdaptation.objects.create(
                            vc_hazard=vc_hazard,
                            stage=stage,
                            province=province,
                            risk_ref=risk,
                            adaptation_strategy_ref=strategy
                        )
                        created_count += 1

                    except Exception as e:
                        skipped += 1
                        self.stderr.write(self.style.ERROR(f"❌ Skipped row due to error: {e}"))

            self.stdout.write(self.style.SUCCESS(f"✅ Successfully imported {created_count} records."))
            if skipped:
                self.stdout.write(self.style.WARNING(f"⚠️ Skipped {skipped} invalid or incomplete rows."))

        except FileNotFoundError:
            self.stderr.write(self.style.ERROR("❌ File not found. Please provide a valid CSV path."))
