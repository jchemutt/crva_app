from django.urls import path
from . import views

urlpatterns = [
    path('api/provinces/', views.province_geojson, name='province_geojson'),
    path('api/strategies/', views.strategy_api, name='strategy_api'),
    path('api/strategies-by-hazard/', views.strategy_by_hazard_view, name='strategy_by_hazard'),
     path('api/timeseries/', views.timeseries_by_province_hazard, name='timeseries_by_province_hazard'),
]
