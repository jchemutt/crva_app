import calendar
import json
import os
import warnings
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from shapely.errors import ShapelyDeprecationWarning
from shapely.geometry import Polygon



warnings.filterwarnings("ignore", category=ShapelyDeprecationWarning)

BASE_DIR = Path(__file__).resolve().parent.parent
f = open(str(BASE_DIR) + '/data.json', )  # Get the data from the data.json file
data = json.load(f)



