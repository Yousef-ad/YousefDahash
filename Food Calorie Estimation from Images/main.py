from fastapi import FastAPI, File, UploadFile, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from PIL import Image
import io
import requests
from typing import Optional

from model.yolov8_food import predict_food

app = FastAPI()

# Serve static folder at "/static"
app.mount("/static", StaticFiles(directory="static"), name="static")

USDA_API_KEY = "RmI0mcs1ZeN0ZbfN97lE6YN0l7FbyvYEShcUvb3A"
USDA_SEARCH_URL = "https://api.nal.usda.gov/fdc/v1/foods/search"

def get_calories_per_100g(food_name: str) -> Optional[float]:
    params = {
        "query": food_name,
        "pageSize": 1,
        "api_key": USDA_API_KEY
    }
    resp = requests.get(USDA_SEARCH_URL, params=params)
    data = resp.json()
    foods = data.get("foods", [])
    if not foods:
        return None

    nutrients = foods[0].get("foodNutrients", [])
    for nutrient in nutrients:
        if "Energy" in nutrient.get("nutrientName", ""):
            return nutrient.get("value")
    return None

@app.get("/")
async def root():
    # Serve the index.html on root URL
    return FileResponse("static/index.html")

@app.post("/detect-food/")
async def detect_food(
    file: UploadFile = File(...),
    serving_size: float = Form(...)
):
    contents = await file.read()
    img = Image.open(io.BytesIO(contents))

    detected_foods = predict_food(img)
    # Remove duplicates by converting list to set, then back to list to preserve unique foods only
    detected_foods = list(set(detected_foods))

    response = []
    for food in detected_foods:
        calories_per_100g = get_calories_per_100g(food)
        if calories_per_100g is None:
            total_calories = None
        else:
            total_calories = (calories_per_100g * serving_size) / 100

        response.append({
            "item": food,
            "calories_per_100g": calories_per_100g,
            "serving_size_grams": serving_size,
            "estimated_calories": total_calories
        })

    return {"food_items": response}
