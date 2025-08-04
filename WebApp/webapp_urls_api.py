from django.urls import path
from . import views

urlpatterns = [
    path('api/provinces/', views.province_geojson, name='province_geojson'),
    path('api/strategies/', views.strategy_api, name='strategy_api'),
    path('api/strategies-by-hazard/', views.strategy_by_hazard_view, name='strategy_by_hazard'),
    path('api/timeseries/', views.timeseries_by_province_hazard, name='timeseries_by_province_hazard'),
    path('api/adaptation-strategies/', views.adaptation_strategies_api, name='api_adaptation_strategies'),
    path('api/implementation-entries/', views.implementation_entries_api, name='api_implementation_entries'),
    path('api/provinces/', views.provinces_api, name='api_provinces'),
    path('api/value-chains/', views.value_chains_api, name='api_value_chains'),
    #path('api/hazards/', views.hazards_api, name='api_hazards'),
    path('api/risk-adaptations/', views.risk_adaptations_api, name='api_risk_adaptations'),
]
