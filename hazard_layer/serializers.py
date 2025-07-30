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
            'geoserver_layer_name',  # <-- add this
            'workspace',             # (optional, if used in your map)
            'store_name',            # (optional)
        ]
