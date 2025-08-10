from rest_framework import serializers
from .models import HazardLayer

class HazardLayerSerializer(serializers.ModelSerializer):
    hazard = serializers.StringRelatedField()
    hazard_id = serializers.PrimaryKeyRelatedField(source='hazard', read_only=True)

    class Meta:
        model = HazardLayer
        fields = [
            'id',
            'hazard',
            'hazard_id',
            'name',
            'scenario',
            'description',
            'geoserver_layer_name',  
            'workspace',            
            'store_name',            
        ]


class IndicatorSerializer(serializers.ModelSerializer):
    # Theme (from Hazard)
    theme = serializers.StringRelatedField(source='hazard')
    theme_id = serializers.PrimaryKeyRelatedField(source='hazard', read_only=True)

    # Component (from Hazard.component)
    component = serializers.SlugRelatedField(
        source='hazard.component', read_only=True, slug_field='key'
    )
    component_label = serializers.CharField(
        source='hazard.component.label', read_only=True
    )

    class Meta:
        model = HazardLayer
        fields = [
            'id',
            'component',          # e.g., 'hazard', 'exposure', 'sensitivity', 'adaptive_capacity'
            'component_label',    # e.g., 'Hazard'
            'theme',              # formerly 'hazard' (string)
            'theme_id',           # formerly 'hazard_id' (PK, read-only)
            'name',
            'scenario',
            'description',
            'geoserver_layer_name',
            'workspace',
            'store_name',
        ]