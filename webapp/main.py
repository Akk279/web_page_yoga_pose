import io
import os
import sys
from typing import Tuple

import numpy as np
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddlewareimage.png
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import json
try:
    # When running as a module (uvicorn webapp.main:app)
    from .lessons_api import router as lessons_router  # type: ignore
    from .gamification.api import router as gamification_router  # type: ignore
    from .auth.api import router as auth_router  # type: ignore
except Exception:
    # When running directly (python webapp/main.py)
    from lessons_api import router as lessons_router  # type: ignore
    from gamification.api import router as gamification_router  # type: ignore
    from auth.api import router as auth_router  # type: ignore
from PIL import Image
import tensorflow as tf


def resource_path(relative_path: str) -> str:
    try:
        base_path = sys._MEIPASS  # type: ignore[attr-defined]
    except Exception:
        # Resolve relative to this file's directory, not the process cwd
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    return os.path.join(base_path, relative_path)


CLASS_NAMES = [
   "Adho Mukha Svanasana",
"Adho Mukha Vrksasana",
"Alanasana",
"Anjaneyasana",
"Ardha Chandrasana",
"Ardha Matsyendrasana",
"Ardha Navasana",
"Ardha Pincha Mayurasana",
"Ashta Chandrasana",
"Baddha Konasana",
"Bakasana",
"Balasana",
"Bitilasana",
"Camatkarasana",
"Dhanurasana",
"Eka Pada Rajakapotasana",
"Garudasana",
"Halasana",
"Hanumanasana",
"Malasana",
"Marjaryasana",
"Navasana",
"Padmasana",
"Parsva Virabhadrasana",
"Parsvottanasana",
"Paschimottanasana",
"Phalakasana",
"Pincha Mayurasana",
"Salamba Bhujangasana",
"Salamba Sarvangasana",
"Setu Bandha Sarvangasana",
"Sivasana",
"Supta Kapotasana",
"Trikonasana",
"Upavistha Konasana",
"Urdhva Dhanurasana",
"Urdhva Mukha Svsnssana",
"Ustrasana",
"Utkatasana",
"Uttanasana",
"Utthita Hasta Padangusthasana",
"Utthita Parsvakonasana",
"Vasisthasana",
"Virabhadrasana One",
"Virabhadrasana Three",
"Virabhadrasana Two",
"Vrksasana"
]


model: tf.keras.Model | None = None


def load_model() -> tf.keras.Model:
    global model
    if model is None:
        model_path = resource_path("yoga_pose_finetuned_model.keras")
        model = tf.keras.models.load_model(model_path)
    return model


def preprocess_image(image: Image.Image) -> np.ndarray:
    image = image.convert("RGB").resize((224, 224))
    img_array = np.array(image, dtype=np.float32) / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    return img_array


def predict_pose_from_image(image: Image.Image) -> Tuple[str, float]:
    mdl = load_model()
    input_tensor = preprocess_image(image)
    preds = mdl.predict(input_tensor, verbose=0)[0]
    idx = int(np.argmax(preds))
    confidence = float(preds[idx])
    pose_name = CLASS_NAMES[idx] if 0 <= idx < len(CLASS_NAMES) else str(idx)
    return pose_name, confidence


app = FastAPI(title="Yoga Pose Analyzer Web API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.isdir(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

    @app.get("/")
    def serve_index():
        index_path = os.path.join(static_dir, "index.html")
        return FileResponse(index_path)

    @app.get("/session")
    def serve_session():
        return FileResponse(os.path.join(static_dir, "session.html"))

    @app.get("/dashboard")
    def serve_dashboard():
        return FileResponse(os.path.join(static_dir, "dashboard.html"))

    @app.get("/shop")
    def serve_shop():
        return FileResponse(os.path.join(static_dir, "shop.html"))

    @app.get("/cart")
    def serve_cart():
        return FileResponse(os.path.join(static_dir, "cart.html"))

    @app.get("/checkout")
    def serve_checkout():
        return FileResponse(os.path.join(static_dir, "checkout.html"))

    @app.get("/book-instructor")
    def serve_book_instructor():
        return FileResponse(os.path.join(static_dir, "book-instructor.html"))

    @app.get("/login")
    def serve_login():
        return FileResponse(os.path.join(static_dir, "login.html"))

    @app.get("/instructions")
    def serve_instructions():
        return FileResponse(os.path.join(static_dir, "instructions.html"))

# Mount the data directory as read-only assets so images/json can be fetched by the frontend
assets_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
if os.path.isdir(assets_dir):
    app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")


def _asanas_dir() -> str:
    # When packaged, base path may shift; reuse resource_path but rooted one level up
    base = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    return os.path.join(base, "data", "asanas")


app.include_router(lessons_router)
app.include_router(gamification_router)
app.include_router(auth_router)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        pose_name, confidence = predict_pose_from_image(image)
        
        # Debug: Get all predictions to see distribution
        mdl = load_model()
        input_tensor = preprocess_image(image)
        preds = mdl.predict(input_tensor, verbose=0)[0]
        
        # Get top 3 predictions for debugging
        top_indices = np.argsort(preds)[-3:][::-1]
        top_predictions = [
            {"pose": CLASS_NAMES[i], "confidence": float(preds[i])} 
            for i in top_indices
        ]
        
        return {
            "pose": pose_name, 
            "confidence": round(confidence, 4),
            "debug_top3": top_predictions
        }
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

