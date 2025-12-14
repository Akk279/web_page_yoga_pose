import os
import json
from fastapi import APIRouter
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

router = APIRouter()


def _base_dir() -> str:
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def _static_dir() -> str:
    return os.path.join(os.path.dirname(__file__), "static")


def _asanas_dir() -> str:
    return os.path.join(_base_dir(), "data", "asanas")


@router.get("/lessons")
def lessons_page():
    static_dir = _static_dir()
    if not os.path.isdir(static_dir):
        return JSONResponse(status_code=404, content={"error": "static dir missing"})
    return FileResponse(os.path.join(static_dir, "lessons.html"))


@router.get("/lessons/data")
def list_lessons():
    asanas_path = _asanas_dir()
    lessons_list: list[dict] = []
    if not os.path.isdir(asanas_path):
        return {"items": lessons_list}

    for folder in sorted(os.listdir(asanas_path)):
        pose_dir = os.path.join(asanas_path, folder)
        if not os.path.isdir(pose_dir):
            continue
        info_path = os.path.join(pose_dir, "info.json")
        info: dict = {}
        try:
            if os.path.isfile(info_path):
                with open(info_path, "r", encoding="utf-8") as f:
                    info = json.load(f)
        except Exception:
            info = {}

        # pick first image if exists
        img_dir = os.path.join(pose_dir, "images")
        image_rel = None
        if os.path.isdir(img_dir):
            for name in os.listdir(img_dir):
                if name.lower().endswith((".png", ".jpg", ".jpeg", ".gif")):
                    image_rel = f"/assets/asanas/{folder}/images/{name}"
                    break

        lessons_list.append({
            "id": folder,
            "name": info.get("name", folder),
            "english_name": info.get("english_name"),
            "description": info.get("description"),
            "image": image_rel,
        })

    return {"items": lessons_list}


def _categories_map() -> dict[str, list[str]]:
    # Exact titles and entries as requested (strings must match lesson keys)
    return {
        "🧘‍♂️ 1. Beginner-Friendly Poses": [
            "Balasana (Child's Pose)",
            "Bitilasana (Cow Pose)",
            "Marjaryasana (Cat Pose)",
            "Tadasana (Mountain Pose)",
            "Padmasana (Lotus Pose)",
            "Baddha Konasana (Butterfly Pose)",
            "Sivasana (Corpse Pose)",
            "Utkatasana (Chair Pose)",
            "Vrksasana (Tree Pose)",
            "Trikonasana (Triangle Pose)",
            "Virabhadrasana One (Warrior I)",
            "Virabhadrasana Two (Warrior II)",
        ],
        "🧘‍♀️ 2. Good for Flexibility": [
            "Hanumanasana (Monkey Pose)",
            "Upavistha Konasana (Wide-Angle Seated Forward Bend)",
            "Uttanasana (Standing Forward Bend)",
            "Parsvottanasana (Pyramid Pose)",
            "Paschimottanasana (Seated Forward Bend)",
            "Urdhva Dhanurasana (Upward-Facing Bow Pose)",
            "Halasana (Plow Pose)",
            "Eka Pada Rajakapotasana (One-Legged King Pigeon Pose)",
            "Ardha Chandrasana (Half Moon Pose)",
            "Ardha Matsyendrasana (Half Lord of the Fishes Pose)",
        ],
        "🧍 3. Good for Spine & Back": [
            "Dhanurasana (Bow Pose)",
            "Urdhva Mukha Svsnssana (Upward-Facing Dog Pose)",
            "Salamba Bhujangasana (Sphinx Pose)",
            "Setu Bandha Sarvangasana (Bridge Pose)",
            "Ardha Matsyendrasana (Half Lord of the Fishes Pose)",
            "Ustrasana (Camel Pose)",
            "Camatkarasana (Wild Thing Pose)",
            "Bitilasana (Cow Pose)",
            "Marjaryasana (Cat Pose)",
        ],
        "🧎 4. Great for Core Strength": [
            "Navasana (Boat Pose)",
            "Ardha Navasana (Half Boat Pose)",
            "Phalakasana (Plank Pose)",
            "Vasisthasana (Side Plank Pose)",
            "Utkatasana (Chair Pose)",
        ],
        "🦵 5. Knee-Friendly / Strengthen Knees": [
            "Utkatasana (Chair Pose)",
            "Virabhadrasana One (Warrior I)",
            "Virabhadrasana Two (Warrior II)",
            "Virabhadrasana Three (Warrior III)",
            "Trikonasana (Triangle Pose)",
            "Utthita Parsvakonasana (Extended Side Angle Pose)",
            "Utthita Hasta Padangusthasana (Extended Hand-to-Big-Toe Pose)",
        ],
        "🧠 6. Good for Balance & Focus": [
            "Vrksasana (Tree Pose)",
            "Ardha Chandrasana (Half Moon Pose)",
            "Garudasana (Eagle Pose)",
            "Utthita Hasta Padangusthasana (Extended Hand-to-Big-Toe Pose)",
            "Vasisthasana (Side Plank Pose)",
            "Bakasana (Crow Pose)",
            "Pincha Mayurasana (Feathered Peacock Pose)",
            "Adho Mukha Vrksasana (Handstand)",
        ],
        "🛏️ 7. Relaxation & Cooling Down": [
            "Balasana (Child's Pose)",
            "Sivasana (Corpse Pose)",
            "Supta Kapotasana (Reclining Pigeon Pose)",
            "Baddha Konasana (Butterfly Pose)",
            "Halasana (Plow Pose)",
        ],
    }


@router.get("/lessons/categories")
def lessons_categories():
    # Build a lookup for multiple display variants per lesson
    all_items = list_lessons()["items"]
    name_to_item: dict[str, dict] = {}
    for it in all_items:
        base_name = (it.get("name") or "").strip()
        eng = (it.get("english_name") or "").strip()
        if base_name:
            name_to_item[base_name] = it
            # Add combined display used by GUI: "Sanskrit (English)"
            if eng:
                name_to_item[f"{base_name} ({eng})"] = it
    grouped: dict[str, list[dict]] = {}
    for title, pose_names in _categories_map().items():
        items: list[dict] = []
        for name in pose_names:
            match = name_to_item.get(name)
            if match:
                items.append(match)
        if items:
            grouped[title] = items
    return grouped


@router.get("/lessons/{lesson_id}")
def lesson_detail_page(lesson_id: str):
    static_dir = _static_dir()
    if not os.path.isdir(static_dir):
        return JSONResponse(status_code=404, content={"error": "static dir missing"})
    return FileResponse(os.path.join(static_dir, "lesson_detail.html"))


@router.get("/lessons/data/{lesson_id}")
def lesson_detail(lesson_id: str):
    pose_dir = os.path.join(_asanas_dir(), lesson_id)
    if not os.path.isdir(pose_dir):
        return JSONResponse(status_code=404, content={"error": "lesson not found"})

    # info
    info: dict = {}
    info_path = os.path.join(pose_dir, "info.json")
    try:
        if os.path.isfile(info_path):
            with open(info_path, "r", encoding="utf-8") as f:
                info = json.load(f)
    except Exception:
        info = {}

    # images
    images: list[str] = []
    img_dir = os.path.join(pose_dir, "images")
    if os.path.isdir(img_dir):
        for name in sorted(os.listdir(img_dir)):
            if name.lower().endswith((".png", ".jpg", ".jpeg", ".gif")):
                images.append(f"/assets/asanas/{lesson_id}/images/{name}")

    return {
        "id": lesson_id,
        "name": info.get("name", lesson_id),
        "english_name": info.get("english_name"),
        "description": info.get("description"),
        "benefits": info.get("benefits", []),
        "youtube_links": info.get("youtube_links", []),
        "images": images,
    }


