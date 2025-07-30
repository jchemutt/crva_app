from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from WebApp.models import Province, ValueChain, Hazard, Stage, ValueChainHazard, RiskAdaptation,ProvinceTimeSeries

# Register the models to the admin site

admin.site.site_header = "CRV App Administration"

admin.site.register(Province)
admin.site.register(ValueChain)
admin.site.register(Hazard)
admin.site.register(Stage)
admin.site.register(ValueChainHazard)
admin.site.register(RiskAdaptation)
admin.site.register(ProvinceTimeSeries)
