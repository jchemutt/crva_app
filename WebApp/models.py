from django.db import models
from django.contrib.gis.db import models as gis_models




class Province(models.Model):
    name = models.CharField(max_length=100, unique=True)
    boundary = gis_models.MultiPolygonField(srid=4326, null=True, blank=True)
    

    def __str__(self):
        return self.name

class ValueChain(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Component(models.Model):
    key = models.SlugField(max_length=40, unique=True)   # e.g., 'hazard', 'exposure'
    label = models.CharField(max_length=80)              # e.g., 'Hazard', 'Exposure'

    class Meta:
        ordering = ["key"]

    def __str__(self):
        return self.label or self.key


class Hazard(models.Model):
    component = models.ForeignKey(
        Component, on_delete=models.PROTECT, related_name='hazards',
        null=True, blank=True  # make non-nullable after data migration, if desired
    )
    name = models.CharField(max_length=100)  # theme name (no global unique)

    class Meta:
        ordering = ["name"]
        unique_together = ("component", "name")  # same theme allowed under different components

    def __str__(self):
        return self.name

class Stage(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class ValueChainHazard(models.Model):
    value_chain = models.ForeignKey(ValueChain, on_delete=models.CASCADE, related_name='hazards')
    hazard = models.ForeignKey(Hazard, on_delete=models.CASCADE, related_name='value_chains')

    class Meta:
        unique_together = ('value_chain', 'hazard')

    def __str__(self):
        return f"{self.value_chain.name} - {self.hazard.name}"
    
class Risk(models.Model):
    description = models.TextField(unique=True)

    def __str__(self):
        return self.description[:80]

class AdaptationStrategy(models.Model):
    description = models.TextField(unique=True)

    def __str__(self):
        return self.description[:80]


class RiskAdaptation(models.Model):
    vc_hazard = models.ForeignKey(ValueChainHazard, on_delete=models.CASCADE, related_name='entries')
    stage = models.ForeignKey(Stage, on_delete=models.CASCADE)
    province = models.ForeignKey(Province, on_delete=models.CASCADE, related_name='adaptations')
    #risk = models.TextField()
    #adaptation_strategy = models.TextField()

    risk_ref = models.ForeignKey(Risk, on_delete=models.SET_NULL, null=True, blank=True)
    adaptation_strategy_ref = models.ForeignKey(AdaptationStrategy, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.province.name} | {self.vc_hazard.value_chain.name} | {self.vc_hazard.hazard.name} | {self.stage.name}"
    


class ProvinceTimeSeries(models.Model):
    province = models.ForeignKey(Province, on_delete=models.CASCADE)
    year = models.IntegerField()
    value = models.FloatField()

    hazard = models.ForeignKey(Hazard, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, blank=True)  # NEW FIELD
    layer = models.ForeignKey('hazard_layer.HazardLayer', on_delete=models.SET_NULL, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('province', 'year', 'hazard', 'layer', 'name')  # Update uniqueness

    def __str__(self):
        return f"{self.province.name} | {self.hazard.name} | {self.name or self.layer} | {self.year} | {self.value}"


class ImplementationStrategy(models.Model):
    title = models.CharField(max_length=255)

    # Updated to link to AdaptationStrategy instead of RiskAdaptation
    adaptation_strategies = models.ManyToManyField(
        'AdaptationStrategy',  # or use the full path if in another module: 'WebApp.AdaptationStrategy'
        related_name='implementation_strategies',
        blank=True
    )

    def __str__(self):
        return self.title


class ImplementationEntry(models.Model):
    strategy = models.ForeignKey(
        ImplementationStrategy,
        on_delete=models.CASCADE,
        related_name='entries'
    )
    proposed_activities = models.TextField(null=True, blank=True)
    timeframe = models.CharField(max_length=255, null=True, blank=True)
    implementers = models.TextField(null=True, blank=True)
    resources_needed = models.TextField(verbose_name="Resources / Investments Needed", null=True, blank=True)
    expected_outcomes = models.TextField(null=True, blank=True)
    beneficiaries = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Entry for {self.strategy.title} - {self.timeframe or 'N/A'}"
