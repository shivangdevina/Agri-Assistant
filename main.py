from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from uuid import uuid4
import logging
from crop_recommendation import llmcalling

# -----------------------------
# Logger
# -----------------------------
logger = logging.getLogger("uvicorn.error")

# -----------------------------
# FastAPI App
# -----------------------------
app = FastAPI(title="Crop Recommendation API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # in production, replace "*" with frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info("Crop Recommendation FastAPI app started with CORS middleware")

# -----------------------------
# Request & Response Models
# -----------------------------
class CropRequest(BaseModel):
    temperature: float
    humidity: float
    rainfall: float
    soilPh: float
    nitrogen: float
    phosphorus: float
    potassium: float
    soilType: str
    season: str


class CropResponse(BaseModel):
    name: str
    percent: int
    short_detail: str
    long_detail: str


# # -----------------------------
# # Dummy Recommendation Logic
# # -----------------------------
# def recommend_crops(data: CropRequest) -> List[CropResponse]:
#     """
#     Replace this mock logic with ML model or database rules later.
#     """

#     # Simple mock rules
#     recs = []

#     if data.temperature > 20 and data.rainfall > 100:
#         recs.append(
#             CropResponse(
#                 name="Tomato",
#                 percent=92,
#                 short_detail="15–20 tons/hectare",
#                 long_detail="Tomatoes thrive in warm climate with good rainfall and neutral soil.",
#             )
#         )

#     if data.soilType.lower() in ["clay", "loam"]:
#         recs.append(
#             CropResponse(
#                 name="Rice",
#                 percent=88,
#                 short_detail="4–6 tons/hectare",
#                 long_detail="Rice grows well in clay/loam soils with adequate water supply.",
#             )
#         )

#     if data.season.lower() in ["summer", "spring"]:
#         recs.append(
#             CropResponse(
#                 name="Corn",
#                 percent=85,
#                 short_detail="8–12 tons/hectare",
#                 long_detail="Corn adapts well to warm seasons and requires moderate rainfall.",
#             )
#         )

#     # Default fallback if no rules matched
#     if not recs:
#         recs.append(
#             CropResponse(
#                 name="Wheat",
#                 percent=75,
#                 short_detail="3–5 tons/hectare",
#                 long_detail="Wheat is a versatile crop suitable for a wide range of conditions.",
#             )
#         )

#     return recs


# -----------------------------
# API Endpoints
# -----------------------------
@app.get("/")
def read_root():
    return {"Hello": "World from Crop API"}

@app.post("/crop", response_model=List[CropResponse])
async def get_crop_recommendations(payload: CropRequest):
    raw = llmcalling(payload.nitrogen, payload.phosphorus, payload.potassium,
                     payload.temperature, payload.humidity, payload.soilPh, payload.rainfall)

    transformed = []
    for item in raw["recommendations"]:
        transformed.append(CropResponse(
            name=item["crop"],                        # map crop → name
            percent=int(item.get("confidence", 0)),   # map confidence → percent
            short_detail=item.get("short_description", ""),
            long_detail=item.get("detailed_description", {}).get("irrigation", "")
        ))
    return transformed
