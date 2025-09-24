from django.contrib import admin
from django.db import models
from django.forms import Textarea
from import_export.admin import ImportExportModelAdmin

from WebApp.models import (
    Province,
    ValueChain,
    Hazard,
    Stage,
    Risk,
    ValueChainHazard,
    RiskAdaptation,
    ProvinceTimeSeries,
    AdaptationStrategy,
    ImplementationStrategy,
    ImplementationEntry,
    Component,
)

admin.site.site_header = "CRV App Administration"

# -----------------------------
# Inline: ImplementationEntry
# -----------------------------
class ImplementationEntryInline(admin.TabularInline):
    model = ImplementationEntry
    extra = 1
    fields = (
        "proposed_activities",
        "timeframe",
        "implementers",
        "resources_needed",
        "expected_outcomes",
        "beneficiaries",
    )
    show_change_link = True

    # Larger text boxes for comfort
    formfield_overrides = {
        models.TextField: {"widget": Textarea(attrs={"rows": 3, "cols": 80})},
    }


# -----------------------------
# ImplementationStrategy Admin
# -----------------------------
@admin.register(ImplementationStrategy)
class ImplementationStrategyAdmin(ImportExportModelAdmin):
    list_display = ("title", "adaptation_strategies_count")
    search_fields = ("title", "adaptation_strategies__description")
    filter_horizontal = ("adaptation_strategies",)  # easy M2M linking in the admin form
    inlines = [ImplementationEntryInline]

    formfield_overrides = {
        models.TextField: {"widget": Textarea(attrs={"rows": 3, "cols": 100})},
    }

    def adaptation_strategies_count(self, obj):
        return obj.adaptation_strategies.count()
    adaptation_strategies_count.short_description = "Linked Adaptation Strategies"


# -----------------------------
# ImplementationEntry Admin
# -----------------------------
@admin.register(ImplementationEntry)
class ImplementationEntryAdmin(ImportExportModelAdmin):
    list_display = ("strategy", "timeframe", "short_activities", "short_outcomes")
    list_filter = ("timeframe",)
    search_fields = (
        "strategy__title",
        "proposed_activities",
        "implementers",
        "expected_outcomes",
        "beneficiaries",
        "resources_needed",
    )

    formfield_overrides = {
        models.TextField: {"widget": Textarea(attrs={"rows": 4, "cols": 100})},
    }

    def short_activities(self, obj):
        txt = obj.proposed_activities or ""
        return (txt[:80] + "…") if len(txt) > 80 else txt
    short_activities.short_description = "Proposed Activities"

    def short_outcomes(self, obj):
        txt = obj.expected_outcomes or ""
        return (txt[:80] + "…") if len(txt) > 80 else txt
    short_outcomes.short_description = "Expected Outcomes"

@admin.register(Risk)
class RiskAdmin(ImportExportModelAdmin):
    list_display = ("short_description",)
    search_fields = ("description",)

    def short_description(self, obj):
        txt = obj.description or ""
        return (txt[:100] + "…") if len(txt) > 100 else txt
    short_description.short_description = "Description"

@admin.register(Component)
class ComponentAdmin(ImportExportModelAdmin):
    list_display = ("key", "label")
    search_fields = ("key", "label")

# -----------------------------
# AdaptationStrategy Admin
# -----------------------------
@admin.register(AdaptationStrategy)
class AdaptationStrategyAdmin(ImportExportModelAdmin):
    list_display = ("short_description", "strategies_count")
    search_fields = ("description",)

    def short_description(self, obj):
        txt = obj.description or ""
        return (txt[:100] + "…") if len(txt) > 100 else txt
    short_description.short_description = "Description"

    def strategies_count(self, obj):
        return obj.implementation_strategies.count()
    strategies_count.short_description = "Implementation Strategies"


# -----------------------------
# RiskAdaptation Admin (normalized)
# -----------------------------
@admin.register(RiskAdaptation)
class RiskAdaptationAdmin(ImportExportModelAdmin):
    list_display = (
        "province",
        "value_chain",
        "hazard",
        "stage",
        "risk_display",
        "adaptation_display",
    )
    list_filter = ("province", "stage", "vc_hazard__hazard__name", "vc_hazard__value_chain__name")
    search_fields = (
        "province__name",
        "vc_hazard__value_chain__name",
        "vc_hazard__hazard__name",
        "risk_ref__description",
        "adaptation_strategy_ref__description",
    )
    # Use raw_id for speed on larger tables; or use autocomplete_fields if you configure search on related admins
    raw_id_fields = ("vc_hazard", "province", "risk_ref", "adaptation_strategy_ref")

    def value_chain(self, obj):
        return obj.vc_hazard.value_chain.name if obj.vc_hazard_id else ""
    value_chain.admin_order_field = "vc_hazard__value_chain__name"

    def hazard(self, obj):
        return obj.vc_hazard.hazard.name if obj.vc_hazard_id else ""
    hazard.admin_order_field = "vc_hazard__hazard__name"

    def risk_display(self, obj):
        return getattr(obj.risk_ref, "description", "")
    risk_display.short_description = "Risk"

    def adaptation_display(self, obj):
        return getattr(obj.adaptation_strategy_ref, "description", "")
    adaptation_display.short_description = "Adaptation Strategy"


# -----------------------------
# Other core models
# -----------------------------
@admin.register(Province)
class ProvinceAdmin(ImportExportModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(ValueChain)
class ValueChainAdmin(ImportExportModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Hazard)
class HazardAdmin(ImportExportModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Stage)
class StageAdmin(ImportExportModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(ValueChainHazard)
class ValueChainHazardAdmin(ImportExportModelAdmin):
    list_display = ("value_chain", "hazard")
    search_fields = ("value_chain__name", "hazard__name")


@admin.register(ProvinceTimeSeries)
class ProvinceTimeSeriesAdmin(ImportExportModelAdmin):
    list_display = ("province", "hazard", "name", "year", "value", "layer")
    list_filter = ("province", "hazard", "name", "layer")
    search_fields = ("province__name", "name")
    raw_id_fields = ("province", "layer")
