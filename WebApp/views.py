import json
from pathlib import Path

from django.contrib import messages
from django.shortcuts import render
from django.templatetags.static import static
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.gis.geos import GEOSGeometry
from WebApp.models import Province, RiskAdaptation,ProvinceTimeSeries
import json
from django.utils.translation import gettext_lazy as _

from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Province, ProvinceTimeSeries
from collections import defaultdict



# Build paths inside the project like this: BASE_DIR / 'subdir'.

BASE_DIR = Path(__file__).resolve().parent.parent
f = open(str(BASE_DIR) + '/data.json', )
data = json.load(f)


def home(request):
    context = {
        "app_cards": [
            {"name": _("Climate Risk & Vulnerability"), "background_image_url": static("images/cards/crva.PNG"),
             'url': reverse('hazard_map')},
            {"name": _("Adaptation Strategies"), "background_image_url": static("images/cards/adaptation.PNG"),
             'url': reverse('adaptation_map')},
            #{"name": _("Agro-Weather Advisory"), "background_image_url": static("images/cards/agro.PNG"),
             #'url': reverse('coming_soon')},
            {"name": _("Implementation Strategies"), "background_image_url": static("images/cards/crop.PNG"),
             'url': reverse('coming_soon')},
            #{"name": _("Market Information"), "background_image_url": static("images/cards/market.PNG"),
             #'url': reverse('coming_soon')},
        ],
    }

    return render(request, 'WebApp/home.html', context)


@csrf_exempt
def select_aoi(request):
    return render(request, 'WebApp/select_aoi.html', {})

@csrf_exempt
def coming_soon(request):
    context = {}
    return render(request, 'WebApp/coming_soon.html', context)


@csrf_exempt
def crva(request):
    context = {}
    return render(request, 'WebApp/crva.html', context)

@csrf_exempt
def map_chart(request):
    context = {}
    return render(request, 'WebApp/map_chart.html', context)


def map_fixed_size(request):
    return render(request, 'WebApp/map_fixedsize.html', {})


def login(request):
    return render(request, 'WebApp/login.html', {})


def map_from_gee(request):
    return render(request, 'WebApp/map_from_GEE.html', {})


def map_full_screen(request):
    return render(request, 'WebApp/map_fullscreen.html', {})


def chart_from_netcdf(request):
    # url = 'https://thredds.servirglobal.net/thredds/wms/mk_aqx/geos/20191123.nc?service=WMS&version=1.3.0&request
    # =GetCapabilities' document = requests.get(url) soup = BeautifulSoup(document.content, "lxml-xml")
    # bounds=soup.find("EX_GeographicBoundingBox") children = bounds.findChildren() bounds_nc=[float(children[
    # 0].get_text()),float(children[1].get_text()),float(children[2].get_text()),float(children[3].get_text())]

    context = {
        "netcdf_path": data["sample_netCDF"],
        # "netcdf_bounds":bounds_nc
    }
    return render(request, 'WebApp/chart_from_netCDF.html', context)


def chart_climateserv(request):
    return render(request, 'WebApp/chart_from_ClimateSERV.html', {})




def about(request):
    return render(request, 'WebApp/about.html', {})


@xframe_options_exempt
def feedback(request):
    return render(request, 'WebApp/feedback.html', {})


def setup(request):
    return render(request, 'WebApp/setup.html', {})




def province_geojson(request):
    features = []

    for province in Province.objects.all():
        risk_data = RiskAdaptation.objects.filter(province=province)
        value_chains = risk_data.values_list('vc_hazard__value_chain__name', flat=True).distinct()
        hazards = risk_data.values_list('vc_hazard__hazard__name', flat=True).distinct()

        if province.boundary:
            features.append({
                "type": "Feature",
                "geometry": json.loads(province.boundary.geojson),
                "properties": {
                    "id": province.id,
                    "name": province.name,
                    "value_chains": list(value_chains),
                    "hazards": list(hazards),
                }
            })

    return JsonResponse({"type": "FeatureCollection", "features": features})



def strategy_api(request):
    province_id = request.GET.get("province")
    value_chain = request.GET.get("value_chain")
    hazard = request.GET.get("hazard")

    qs = RiskAdaptation.objects.filter(
        province_id=province_id,
        vc_hazard__value_chain__name=value_chain,
        vc_hazard__hazard__name=hazard
    ).select_related('stage')

    data = [
        {
            "stage": r.stage.name,
            "risk": r.risk_ref.description if r.risk_ref else None,
            "strategy": r.adaptation_strategy_ref.description if r.adaptation_strategy_ref else None
        } for r in qs
    ]

    return JsonResponse(data, safe=False)



def strategy_by_hazard_view(request):
    hazard_id = request.GET.get("hazard")      # actual foreign key ID from dataset
    province_name = request.GET.get("province")

    qs = RiskAdaptation.objects.filter(
        province__name__iexact=province_name,
        vc_hazard__hazard_id=hazard_id
    ).select_related('stage', 'vc_hazard__value_chain', 'vc_hazard__hazard')

    data = [
        {
            "value_chain": r.vc_hazard.value_chain.name,
            "hazard": r.vc_hazard.hazard.name,
            "stage": r.stage.name,
            "risk": r.risk_ref.description if r.risk_ref else None,
            "strategy": r.adaptation_strategy_ref.description if r.adaptation_strategy_ref else None
        } for r in qs
    ]

    return JsonResponse(data, safe=False)

@api_view(['GET'])
def timeseries_by_province_hazard(request):
    province_name = request.GET.get('province')
    hazard_id = request.GET.get('hazard')

    if not province_name or not hazard_id:
        return Response({"error": "Missing 'province' or 'hazard' parameter."}, status=400)

    try:
        province = Province.objects.get(name=province_name)
    except Province.DoesNotExist:
        return Response({"error": f"Province '{province_name}' not found."}, status=404)

    queryset = ProvinceTimeSeries.objects.filter(
        province=province,
        hazard_id=hazard_id
    ).order_by('year')

    grouped = defaultdict(lambda: {"layer_name": None, "data": []})

    for entry in queryset:
        group_name = entry.name or "Unnamed Group"
        layer_name = entry.layer.name if entry.layer else None
        grouped[group_name]["layer_name"] = layer_name
        grouped[group_name]["data"].append({
            "year": entry.year,
            "value": entry.value
        })

    return Response(grouped)

def adaptation_map_view(request):
    return render(request, 'WebApp/adaptation_map.html')

def hazard_map_view(request):
    return render(request, 'WebApp/hazard_map.html')

