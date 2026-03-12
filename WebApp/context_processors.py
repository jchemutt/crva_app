from django.conf import settings

def app_config(request):
    return {
        "GEOSERVER_URL": getattr(settings, "GEOSERVER_URL", ""),
    }