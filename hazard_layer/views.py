from rest_framework import viewsets, mixins
from django_large_image.rest import LargeImageFileDetailMixin
from .models import HazardLayer
from .serializers import HazardLayerSerializer

class HazardLayerViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
    LargeImageFileDetailMixin,
):
    queryset = HazardLayer.objects.all()
    serializer_class = HazardLayerSerializer
    FILE_FIELD_NAME = 'file'  # Make sure this matches your model's field
