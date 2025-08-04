from rest_framework import viewsets, mixins
from .models import HazardLayer
from .serializers import HazardLayerSerializer

class HazardLayerViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = HazardLayer.objects.all()
    serializer_class = HazardLayerSerializer
