from rest_framework import viewsets, mixins,filters
from .models import HazardLayer
from .serializers import HazardLayerSerializer,IndicatorSerializer

class HazardLayerViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = HazardLayer.objects.all()
    serializer_class = HazardLayerSerializer


class IndicatorViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """
    Read-only endpoint for indicator layers.
    Supports filtering by component (key) and theme (id or name).
    """
    serializer_class = IndicatorSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "scenario", "description", "hazard__name", "geoserver_layer_name"]
    ordering_fields = ["name", "scenario", "geoserver_layer_name"]
    ordering = ["name"]

    def get_queryset(self):
        qs = (
            HazardLayer.objects
            .select_related("hazard", "hazard__component")   # <— efficient joins
            .all()
        )

        # ---- Optional filters via query params ----
        comp = self.request.query_params.get("component")         # e.g. 'hazard', 'exposure'
        theme_id = self.request.query_params.get("theme_id")      # hazard pk
        theme = self.request.query_params.get("theme")            # hazard name
        scenario = self.request.query_params.get("scenario")      # e.g. 'ssp585'

        if comp:
            qs = qs.filter(hazard__component__key=comp)
        if theme_id:
            qs = qs.filter(hazard_id=theme_id)
        if theme:
            qs = qs.filter(hazard__name__iexact=theme)
        if scenario:
            qs = qs.filter(scenario__iexact=scenario)

        return qs    
