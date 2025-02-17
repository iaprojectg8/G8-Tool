
# Utils 
import time
import os
import tempfile
import pandas as pd 
import geopandas as gpd
import numpy as np
import random as rd
import math
import io
import zipfile
import shutil
import time
from tqdm import tqdm
from copy import copy
import ast
import streamlit as st
import xarray as xr
from zipfile import ZipFile
from send2trash import send2trash
import re

# Date and time
from datetime import datetime, date
import pytz


# Plot part
import plotly.graph_objects as go
from scipy.stats import linregress
import plotly.express as px
import plotly.io as pio
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.utils import ImageReader


# Map part
from pyproj import CRS
from shapely.geometry import Polygon, mapping, Point
from shapely.geometry import Point
import folium
from folium.plugins import MeasureControl
from folium import raster_layers
from streamlit_folium import st_folium



# Raster viz part
from rasterio.transform import from_origin
from rasterio import MemoryFile
from rasterio.features import geometry_mask
from scipy.interpolate import griddata


# Request part
import requests
import openmeteo_requests 
import requests_cache
from retry_requests import retry


# Test part
import pytest
from unittest import mock
from unittest.mock import MagicMock