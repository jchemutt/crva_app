from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from rest_framework.routers import DefaultRouter
from hazard_layer.views import HazardLayerViewSet,IndicatorViewSet
from django.conf.urls.i18n import i18n_patterns
from django.views.i18n import set_language
from django.conf import settings
from django.conf.urls.static import static

router = DefaultRouter()
router.register(r'hazards', HazardLayerViewSet, basename='hazardlayer')
router.register(r'indicators', IndicatorViewSet, basename='indicator')



# APIs — no translation
urlpatterns = [
    path('set-language/', set_language, name='set_language'),
    path('', include('WebApp.webapp_urls_api')),  # non-translatable
    path('api/', include(router.urls)),
    path('admin/', admin.site.urls),
]

# Public UI — translatable
urlpatterns += i18n_patterns(
    path('', include('WebApp.webapp_urls_translatable')),
    path('accounts/', include('allauth.urls')),
    
)

# 

    
