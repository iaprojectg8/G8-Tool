
import time
import os
from pyproj import CRS
import pandas as pd 
from datetime import datetime, date
import calendar
import json
from shapely.geometry import Polygon, mapping, Point
import shapely
import requests
import geopandas as gpd
import tempfile
import numpy as np
import random as rd
import math
import io

import base64
import matplotlib.pyplot as plt
from matplotlib import rcParams
from matplotlib.backend_bases import MouseEvent
import time
from tqdm import tqdm
from copy import copy
import ast


# Raster viz part
import rasterio
from rasterio.transform import from_origin
from rasterio import MemoryFile
from scipy.interpolate import griddata
from rasterio.features import geometry_mask
from ipywidgets import interactive
from matplotlib.widgets import Slider
from scipy.spatial import KDTree

# Streamlit part
import streamlit as st


# Test part
import pytest
from unittest import mock
from unittest.mock import MagicMock

# Plot part
import plotly.graph_objects as go
import pytz
# Regression part
from scipy.stats import linregress
import plotly.express as px
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, A4
import plotly.io as pio
from reportlab.lib.utils import ImageReader
from math import *

# Map part

import folium
import leafmap
from folium.plugins import MeasureControl
from shapely.geometry import Point
from folium import raster_layers
from streamlit_folium import st_folium
import zipfile
import shutil
import glob



# Request part

import requests
import openmeteo_requests 
import requests_cache
from retry_requests import retry
import xarray as xr