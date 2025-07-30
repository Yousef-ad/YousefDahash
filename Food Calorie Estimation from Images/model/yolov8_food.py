from ultralytics import YOLO
from PIL import Image

# Load YOLOv8n model once
model = YOLO("yolov8n.pt")

def predict_food(image: Image.Image, conf_threshold=0.5):
    results = model(image)
    detected_foods = []

    for r in results:
        for box in r.boxes:
            if box.conf < conf_threshold:
                continue  # skip low confidence predictions

            class_id = int(box.cls)
            class_name = model.names[class_id]
            detected_foods.append(class_name)

    return detected_foods
