# app/gee_utils.py
import os
import uuid
import requests
import ee
from dotenv import load_dotenv

# -------------------------------
# Load environment variables
# -------------------------------
load_dotenv()

EE_SERVICE_ACCOUNT = os.getenv("EE_SERVICE_ACCOUNT")
EE_PRIVATE_KEY_FILE = os.getenv("EE_PRIVATE_KEY_FILE", "./ee-key.json")

# Default results directory
RESULTS_DIR = os.getenv("RESULTS_DIR", "./results")

# Thumbnail scale
THUMBNAIL_SCALE = int(os.getenv("THUMBNAIL_SCALE", "30"))

# Ensure results folder exists
os.makedirs(RESULTS_DIR, exist_ok=True)


# -------------------------------
# Initialize Earth Engine
# -------------------------------
def init_ee():
    """
    Initialize Google Earth Engine using service account or default auth.
    """
    try:
        if EE_SERVICE_ACCOUNT and EE_PRIVATE_KEY_FILE and os.path.exists(EE_PRIVATE_KEY_FILE):
            creds = ee.ServiceAccountCredentials(
                EE_SERVICE_ACCOUNT,
                EE_PRIVATE_KEY_FILE
            )
            ee.Initialize(creds)
            print("✔ Earth Engine initialized with Service Account")
        else:
            ee.Initialize()
            print("✔ Earth Engine initialized with User Auth")
    except Exception as e:
        raise RuntimeError(f"Earth Engine initialization failed: {e}")


# -------------------------------
# Main Processing Function
# -------------------------------
def compute_ndvi_zscore_and_vectors(aoi_geojson, start_date, end_date, satellite="sentinel_2"):
    """
    1. Load Sentinel-2 SR
    2. Compute NDVI
    3. Compute NDVI z-score
    4. Detect anomaly mask (z < -2)
    5. Convert anomalies → vectors → getDownloadURL()
    6. Generate thumbnail
    """

    # Convert AOI to Earth Engine geometry
    geom = ee.Geometry(aoi_geojson)

    # ----------------------------------------------------
    # Load Sentinel-2 Surface Reflectance (NO QA60 band)
    # ----------------------------------------------------
    if satellite.lower().startswith("sentinel"):
        col = (
            ee.ImageCollection("COPERNICUS/S2_SR")
            .filterBounds(geom)
            .filterDate(start_date, end_date)
            .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 40))
        )

        # SCL → Scene Classification Layer (cloud mask)
        def mask_s2(img):
            scl = img.select("SCL")
            # Keep good classes: vegetation, bare soil, water, etc.
            mask = scl.remap(
                [3, 4, 5, 6, 7, 11],   # Allowed SCL classes
                [1, 1, 1, 1, 1, 1],
                0
            )
            return img.updateMask(mask)

        col = col.map(mask_s2)

        def add_ndvi(img):
            nd = img.normalizedDifference(["B8", "B4"]).rename("NDVI")
            return img.addBands(nd)

        col_ndvi = col.map(add_ndvi).select("NDVI")

    else:
        raise ValueError("Only Sentinel-2 supported currently.")

    # ----------------------------------------------------
    # Compute baseline mean & std
    # ----------------------------------------------------
    ndvi_mean = col_ndvi.mean()
    ndvi_std = col_ndvi.reduce(ee.Reducer.stdDev())

    # Latest NDVI image
    latest = ee.Image(col_ndvi.sort("system:time_start", False).first())

    # Z-score = (latest - mean) / std
    zscore = (
        latest.subtract(ndvi_mean)
        .divide(ndvi_std.add(ee.Image.constant(1e-6)))
        .rename("zscore")
    )

    # Anomaly mask = z < -2
    anomaly_mask = zscore.lt(-2).selfMask().rename("anomaly")

    # ----------------------------------------------------
    # Convert raster → vector polygons (safe settings)
    # ----------------------------------------------------
    vectors = anomaly_mask.reduceToVectors(
        geometry=geom,
        scale=10,
        geometryType="polygon",
        eightConnected=True,
        maxPixels=1e7,
        bestEffort=True,
        tileScale=4
    )

    # Instead of getInfo() → return download URL
    try:
        vectors_url = vectors.getDownloadURL("geojson")
    except Exception as e:
        raise RuntimeError(f"ERROR: reduceToVectors failed. AOI too large. {e}")

    # ----------------------------------------------------
    # Generate thumbnail
    # ----------------------------------------------------
    vis_params = {
        "min": -3,
        "max": 3,
        "palette": ["00ff00", "ffff00", "ff0000"],
    }

    try:
        thumb_url = zscore.getThumbURL(
            {
                "min": vis_params["min"],
                "max": vis_params["max"],
                "palette": vis_params["palette"],
                "region": geom,
                "scale": THUMBNAIL_SCALE,
                "format": "png",
            }
        )
    except Exception:
        thumb_url = None

    # Download thumbnail locally
    local_thumb_path = None
    if thumb_url:
        try:
            resp = requests.get(thumb_url, timeout=60)
            if resp.status_code == 200:
                fname = f"zscore_{uuid.uuid4().hex}.png"
                local_thumb_path = os.path.join(RESULTS_DIR, fname)
                with open(local_thumb_path, "wb") as f:
                    f.write(resp.content)
        except Exception:
            local_thumb_path = None

    # -------------------------------
    # Return download URL + thumbnail
    # -------------------------------
    return vectors_url, local_thumb_path
