from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

import WebApp.views as views
from WebApp import api_handlers

urlpatterns = [
    path('', views.home, name='home'),
    path('coming_soon/', views.coming_soon, name='coming_soon'),
    path('crva/', views.crva, name='crva'),
    path('adaptation/', views.adaptation_map_view, name='adaptation_map'),
    path('hazard_map/', views.hazard_map_view, name='hazard_map'),
    path('implementation-strategies/', views.implementation_strategies_view, name='implementation_strategies'),
    path('risk-adaptations/', views.risk_adaptations_view, name='risk_adaptations'),
    
    path('about/', views.about, name='about'),
    path('login/', views.login, name='login'),
    path('setup/', views.setup, name='setup'),
    path('feedback/', views.feedback, name='feedback'),
    

]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
