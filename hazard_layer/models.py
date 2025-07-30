from django.db import models

class HazardLayer(models.Model):
    name = models.CharField(max_length=100)
    scenario = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)

    # Instead of FileField, store GeoServer layer name
    geoserver_layer_name = models.CharField(
        max_length=150, help_text="e.g. crva:drought_2021_scenario1"
    )
    workspace = models.CharField(max_length=100, default="crva")
    store_name = models.CharField(max_length=100, blank=True)

    hazard = models.ForeignKey('WebApp.Hazard', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.scenario or 'Default'}"
