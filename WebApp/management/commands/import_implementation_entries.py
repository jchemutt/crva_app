import csv
from pathlib import Path
from django.core.management.base import BaseCommand
from django.db import transaction
from WebApp.models import ImplementationStrategy, ImplementationEntry, AdaptationStrategy

def _clean(val):
    if val is None:
        return ""
    return str(val).strip().strip('"').strip("'")

def _read_csv(path):
    path = Path(path)
    for enc in ("utf-8-sig", "utf-8", "ISO-8859-1"):
        try:
            f = path.open(newline='', encoding=enc)
            reader = csv.DictReader(f)
            _ = reader.fieldnames
            return f, reader
        except Exception:
            continue
    raise RuntimeError("Could not read CSV with utf-8/utf-8-sig/ISO-8859-1")

class Command(BaseCommand):
    help = "Import ImplementationEntry rows from a CSV; get_or_create ImplementationStrategy by strategy_title. Optionally link AdaptationStrategy(s) if 'adaptation_strategies' column exists."

    def add_arguments(self, parser):
        parser.add_argument("csv_file", type=str, help="Path to the entries CSV file")
        parser.add_argument("--replace-entries", action="store_true",
                            help="If set, delete existing entries for a strategy before importing rows for that strategy.")

    @transaction.atomic
    def handle(self, *args, **opts):
        path = opts["csv_file"]
        replace_entries = opts["replace_entries"]

        fh, reader = _read_csv(path)
        try:
            cols = {c.lower(): c for c in (reader.fieldnames or [])}
            if "strategy_title" not in cols:
                raise ValueError("CSV must include 'strategy_title' column.")

            created_strategies = 0
            created_entries = 0
            linked_adapt = 0
            seen_to_replace = set()

            for row in reader:
                stitle = _clean(row[cols["strategy_title"]])
                if not stitle:
                    self.stderr.write(self.style.WARNING("Skipped row: empty strategy_title"))
                    continue

                strategy, s_created = ImplementationStrategy.objects.get_or_create(title=stitle)
                if s_created:
                    created_strategies += 1

                # Replace entries once per strategy if requested
                if replace_entries and stitle not in seen_to_replace:
                    deleted, _ = ImplementationEntry.objects.filter(strategy=strategy).delete()
                    if deleted:
                        self.stdout.write(self.style.WARNING(
                            f"Deleted {deleted} existing entries for strategy '{stitle}'"
                        ))
                    seen_to_replace.add(stitle)

                # Optional: link adaptation strategies if the column exists
                if "adaptation_strategies" in cols:
                    raw = _clean(row.get(cols["adaptation_strategies"], ""))
                    if raw:
                        for desc in [p.strip() for p in raw.split(";") if p.strip()]:
                            aobj, _ = AdaptationStrategy.objects.get_or_create(description=desc)
                            if not strategy.adaptation_strategies.filter(pk=aobj.pk).exists():
                                strategy.adaptation_strategies.add(aobj)
                                linked_adapt += 1

                entry = ImplementationEntry.objects.create(
                    strategy=strategy,
                    proposed_activities=_clean(row.get(cols.get("proposed_activities", ""), "")),
                    timeframe=_clean(row.get(cols.get("timeframe", ""), "")),
                    implementers=_clean(row.get(cols.get("implementers", ""), "")),
                    resources_needed=_clean(row.get(cols.get("resources_needed", ""), "")),
                    expected_outcomes=_clean(row.get(cols.get("expected_outcomes", ""), "")),
                    beneficiaries=_clean(row.get(cols.get("beneficiaries", ""), "")),
                )
                created_entries += 1

        finally:
            fh.close()

        self.stdout.write(self.style.SUCCESS(
            f"Done. Strategies created: {created_strategies}, entries created: {created_entries}, "
            f"adaptation-strategy links added: {linked_adapt}"
        ))
