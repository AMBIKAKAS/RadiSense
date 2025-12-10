# app/main.py
import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from app.schemas import AnalysisRequest
from app import gee_utils
import ee

RESULTS_DIR = os.environ.get("RESULTS_DIR", "results")
os.makedirs(RESULTS_DIR, exist_ok=True)

app = FastAPI(title="Radiation Anomaly Detector (GEE baseline)")

app.mount("/results", StaticFiles(directory=RESULTS_DIR), name="results")


@app.get("/api/v1/health")
def health():
    return {"status": "ok"}


@app.post("/api/v1/analyze")
async def analyze(req: AnalysisRequest):

    # Ensure Earth Engine is initialized
    try:
        ee.data.getInfo()
    except Exception:
        try:
            gee_utils.init_ee()
            print("✔ Earth Engine re-initialized")
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Earth Engine init error: {e}"
            )

    aoi = req.aoi.dict()   # <<< IMPORTANT FIX
    start_date = req.start_date
    end_date = req.end_date
    satellite = req.satellite or "sentinel_2"

    if not aoi or not start_date or not end_date:
        raise HTTPException(status_code=400, detail="Missing aoi or date range")

    # Run anomaly detection
    try:
        vectors_geojson, local_thumb_path = gee_utils.compute_ndvi_zscore_and_vectors(
            aoi_geojson=aoi,
            start_date=start_date,
            end_date=end_date,
            satellite=satellite
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # Count polygons
    num_polygons = 0
    if isinstance(vectors_geojson, dict):
        num_polygons = len(vectors_geojson.get("features", []))

    # Build thumbnail public URL
    thumbnail_url = None
    if local_thumb_path:
        thumbnail_url = "/results/" + os.path.basename(local_thumb_path)

    return JSONResponse(
        content={
            "status": "success",
            "summary": {
                "num_polygons": num_polygons
            },
            "polygons": vectors_geojson,
            "thumbnail_url": thumbnail_url
        }
    )


@app.get("/api/v1/results/{filename}")
def get_result_file(filename: str):
    filepath = os.path.join(RESULTS_DIR, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(filepath, media_type="image/png")
