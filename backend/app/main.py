import ee
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.schemas import AnalysisRequest
from app.gee_utils import init_ee, detect_radiation_signals

# ================= FASTAPI APP =================
app = FastAPI(
    title="RadiSense – Radiation Leak Detection API",
    version="1.0.0"
)

# ================= CORS (CRITICAL FIX) =================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js frontend
    allow_credentials=True,
    allow_methods=["*"],  # allows OPTIONS, POST, GET
    allow_headers=["*"],
)

# ================= HEALTH CHECK =================
@app.get("/api/v1/health")
def health():
    return {"status": "ok"}

# ================= ANALYSIS ENDPOINT =================
@app.post("/api/v1/analyze")
async def analyze(req: AnalysisRequest):
    # Ensure Earth Engine is initialized
    try:
        ee.data.getInfo()
    except Exception:
        init_ee()

    try:
        result = detect_radiation_signals(
            aoi=req.aoi.dict(),
            start=req.start_date,
            end=req.end_date
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Detection failed: {e}"
        )

    return JSONResponse(
        content={
            "status": "success",
            "risk_score": result["risk_score"],
            "risk_level": result["risk_level"],
            "anomaly_vectors": result["vectors"]
        }
    )
