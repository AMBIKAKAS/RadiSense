from pydantic import BaseModel
from typing import Literal, List

class AOI(BaseModel):
    type: Literal["Polygon"]
    coordinates: List[List[List[float]]]

class AnalysisRequest(BaseModel):
    aoi: AOI
    start_date: str
    end_date: str
    satellite: str = "sentinel_2"
