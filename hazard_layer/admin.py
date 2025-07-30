from django.contrib import admin
from .models import HazardLayer

@admin.register(HazardLayer)
class HazardLayerAdmin(admin.ModelAdmin):
    list_display = ("name", "hazard", "scenario", "geoserver_layer_name", "created_at")
    search_fields = ("name", "scenario", "geoserver_layer_name")
    list_filter = ("hazard",)
    ordering = ("-created_at",)
