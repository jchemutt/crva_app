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

from WebApp.models import (
    Province, ValueChain, Hazard, Stage,
    ValueChainHazard, Risk, AdaptationStrategy, RiskAdaptation,
    ProvinceTimeSeries,ImplementationStrategy, 
    ImplementationEntry
)
import json
from django.utils.translation import gettext_lazy as _

from rest_framework.decorators import api_view
from rest_framework.response import Response

from collections import defaultdict

from django.db.models import Prefetch, Q  # for filtering
from django.views.decorators.http import require_GET
from django.contrib.postgres.aggregates import ArrayAgg

import json
from collections import defaultdict
from django.http import JsonResponse
from django.contrib.gis.db.models.functions import PointOnSurface, Transform, AsGeoJSON

from django.db.models import Value, CharField
from django.db.models.functions import Concat







# Build paths inside the project like this: BASE_DIR / 'subdir'.

BASE_DIR = Path(__file__).resolve().parent.parent
f = open(str(BASE_DIR) + '/data.json', )
data = json.load(f)


def home(request):
    context = {
        "app_cards": [
            {"name": _("Climate Risk & Vulnerability"), "background_image_url": static("images/cards/crva.png"),
             'url': reverse('hazard_map')},
            {"name": _("Adaptation Strategies"), "background_image_url": static("images/cards/adaptation.png"),
             'url': reverse('adaptation_map')},
            #{"name": _("Agro-Weather Advisory"), "background_image_url": static("images/cards/agro.png"),
             #'url': reverse('coming_soon')},
            {"name": _("Implementation Strategies"), "background_image_url": static("images/cards/crop.png"),
             'url': reverse('implementation_strategies')},
            #{"name": _("Market Information"), "background_image_url": static("images/cards/market.png"),
             #'url': reverse('coming_soon')},
        ],
    }

    return render(request, 'WebApp/home.html', context)



@csrf_exempt
def coming_soon(request):
    context = {}
    return render(request, 'WebApp/coming_soon.html', context)


@csrf_exempt
def crva(request):
    context = {}
    return render(request, 'WebApp/crva.html', context)


def login(request):
    return render(request, 'WebApp/login.html', {})



def implementation_strategies_view(request):
    """
    Renders the UI page (DataTable + filters) for Implementation Strategies.
    """
    return render(request, 'WebApp/implementation_strategies.html')




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





# views.py



@require_GET
def province_summaries(request):
    """
    Geometry-free summaries for the map overlay.
    Returns: [
      {
        id, name,
        centroid: {lat, lng},
        value_chains: [..],
        hazards: [..],
        hazards_by_vc: { "<VC>": ["Hazard1", ...], ... }
      }, ...
    ]
    """

    # Build distinct arrays:
    #  - value_chains_arr
    #  - hazards_arr
    #  - vc_hz_pairs as "VC|||HZ" strings (since JSONObject isn't available)
    qs = (
        Province.objects
        .filter(boundary__isnull=False)
        .annotate(_pt=PointOnSurface('boundary'))
        .annotate(_pt4326=Transform('_pt', 4326))
        .annotate(ptjson=AsGeoJSON('_pt4326'))
        .annotate(
            value_chains_arr=ArrayAgg(
                'adaptations__vc_hazard__value_chain__name',
                distinct=True
            ),
            hazards_arr=ArrayAgg(
                'adaptations__vc_hazard__hazard__name',
                distinct=True
            ),
            vc_hz_pairs=ArrayAgg(
                Concat(
                    'adaptations__vc_hazard__value_chain__name',
                    Value('|||'),
                    'adaptations__vc_hazard__hazard__name',
                    output_field=CharField()
                ),
                distinct=True
            ),
        )
        .values('id', 'name', 'ptjson', 'value_chains_arr', 'hazards_arr', 'vc_hz_pairs')
    )

    out = []
    for r in qs:
        # Extract centroid from GeoJSON (coordinates = [lng, lat])
        lat = lng = None
        if r['ptjson']:
            try:
                coords = json.loads(r['ptjson']).get('coordinates')  # [lng, lat]
                if isinstance(coords, (list, tuple)) and len(coords) == 2:
                    lng, lat = float(coords[0]), float(coords[1])
            except Exception:
                pass

        vc_list = [v for v in (r['value_chains_arr'] or []) if v]
        hz_list = [h for h in (r['hazards_arr'] or []) if h]

        # Build hazards_by_vc from "VC|||HZ" pairs
        hazards_by_vc = defaultdict(list)
        for s in (r['vc_hz_pairs'] or []):
            if not s:
                continue
            try:
                vc, hz = s.split('|||', 1)
            except ValueError:
                continue
            if vc and hz and hz not in hazards_by_vc[vc]:
                hazards_by_vc[vc].append(hz)

        out.append({
            "id": r["id"],
            "name": r["name"],
            "centroid": {"lat": lat, "lng": lng},
            "value_chains": vc_list,
            "hazards": hz_list,
            "hazards_by_vc": dict(hazards_by_vc),
        })

    return JsonResponse(out, safe=False)




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

@api_view(['GET'])
def adaptation_strategies_api(request):
    """
    Returns [{id, description}, ...] for populating the Adaptation Strategy filter.
    """
    qs = AdaptationStrategy.objects.order_by('description').only('id', 'description')
    data = [{"id": a.id, "description": a.description} for a in qs]
    return Response(data)

@api_view(['GET'])
def implementation_entries_api(request):
    """
    Returns a flat list of ImplementationEntry rows for DataTables.

    Query params:
      q=keyword
      timeframe=Short-term|Medium-term|Long-term (repeatable)
      adapt_ids=1,2,3 (M2M AdaptationStrategy ids)
    """
    q = (request.GET.get('q') or '').strip()
    timeframe_vals = request.GET.getlist('timeframe')  # may be multiple
    adapt_ids_raw = (request.GET.get('adapt_ids') or '').strip()
    adapt_ids = [int(x) for x in adapt_ids_raw.split(',') if x.strip().isdigit()]

    qs = (
        ImplementationEntry.objects
        .select_related('strategy')
        .prefetch_related(
            Prefetch(
                'strategy__adaptation_strategies',
                queryset=AdaptationStrategy.objects.only('id', 'description')
            )
        )
        .all()
    )

    if q:
        qs = qs.filter(
            Q(strategy__title__icontains=q) |
            Q(proposed_activities__icontains=q) |
            Q(implementers__icontains=q) |
            Q(resources_needed__icontains=q) |
            Q(expected_outcomes__icontains=q) |
            Q(beneficiaries__icontains=q) |
            Q(strategy__adaptation_strategies__description__icontains=q)
        ).distinct()

    if timeframe_vals:
        qs = qs.filter(timeframe__in=timeframe_vals)

    if adapt_ids:
        qs = qs.filter(strategy__adaptation_strategies__id__in=adapt_ids).distinct()

    qs = qs.order_by('strategy__title', 'timeframe', 'id')

    data = []
    for e in qs:
        data.append({
            "id": e.id,
            "strategy": e.strategy_id,
            "strategy_title": e.strategy.title if e.strategy_id else "",
            "timeframe": e.timeframe or "",
            "proposed_activities": e.proposed_activities or "",
            "implementers": e.implementers or "",
            "resources_needed": e.resources_needed or "",
            "expected_outcomes": e.expected_outcomes or "",
            "beneficiaries": e.beneficiaries or "",
            "adaptation_strategies": [
                {"id": a.id, "description": a.description}
                for a in e.strategy.adaptation_strategies.all()
            ] if e.strategy_id else []
        })

    return Response(data)

# ---------- Page view ----------
def risk_adaptations_view(request):
    """
    Renders the Risk Adaptations table page (DataTables + filters).
    """
    return render(request, 'WebApp/risk_adaptations.html')


# ---------- Lookup endpoints for filters ----------
@api_view(['GET'])
def provinces_api(request):
    qs = Province.objects.order_by('name').only('id', 'name')
    return Response([{"id": p.id, "name": p.name} for p in qs])

@api_view(['GET'])
def value_chains_api(request):
    qs = ValueChain.objects.order_by('name').only('id', 'name')
    return Response([{"id": v.id, "name": v.name} for v in qs])

'''@api_view(['GET'])
def hazards_api(request):
    qs = Hazard.objects.order_by('name').only('id', 'name')
    return Response([{"id": h.id, "name": h.name} for h in qs])'''


# ---------- Main data endpoint ----------
@api_view(['GET'])
def risk_adaptations_api(request):
    """
    Returns a flat list of RiskAdaptation rows with optional filters.

    Query params:
      q=keyword (search in risk, strategy, stage, province, vc, hazard)
      province=<id>
      value_chain=<id>
      hazard=<id>
      stage=<id>  (optional)
    """
    q = (request.GET.get('q') or '').strip()

    province_id = request.GET.get('province')
    value_chain_id = request.GET.get('value_chain')
    hazard_id = request.GET.get('hazard')
    stage_id = request.GET.get('stage')

    qs = (
        RiskAdaptation.objects
        .select_related(
            'province', 'stage',
            'vc_hazard__value_chain', 'vc_hazard__hazard',
            'risk_ref', 'adaptation_strategy_ref'
        )
        .all()
    )

    if province_id and province_id.isdigit():
        qs = qs.filter(province_id=int(province_id))
    if value_chain_id and value_chain_id.isdigit():
        qs = qs.filter(vc_hazard__value_chain_id=int(value_chain_id))
    if hazard_id and hazard_id.isdigit():
        qs = qs.filter(vc_hazard__hazard_id=int(hazard_id))
    if stage_id and stage_id.isdigit():
        qs = qs.filter(stage_id=int(stage_id))

    if q:
        qs = qs.filter(
            Q(province__name__icontains=q) |
            Q(vc_hazard__value_chain__name__icontains=q) |
            Q(vc_hazard__hazard__name__icontains=q) |
            Q(stage__name__icontains=q) |
            Q(risk_ref__description__icontains=q) |
            Q(adaptation_strategy_ref__description__icontains=q)
        ).distinct()

    qs = qs.order_by('vc_hazard__value_chain__name', 'vc_hazard__hazard__name', 'province__name', 'stage__name', 'id')

    data = []
    for ra in qs:
        data.append({
            "id": ra.id,
            "province": ra.province.name if ra.province_id else "",
            "value_chain": ra.vc_hazard.value_chain.name if ra.vc_hazard_id else "",
            "hazard": ra.vc_hazard.hazard.name if ra.vc_hazard_id else "",
            "stage": ra.stage.name if ra.stage_id else "",
            "risk": getattr(ra.risk_ref, 'description', "") or "",
            "adaptation_strategy": getattr(ra.adaptation_strategy_ref, 'description', "") or "",
        })
    return Response(data)


