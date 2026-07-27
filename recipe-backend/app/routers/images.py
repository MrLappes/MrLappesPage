"""Image storage: uploads are validated, stripped of metadata, downscaled and
re-encoded to WEBP, then stored as BLOBs in SQLite. Served publicly by id.
"""
import base64
import binascii
import io

from fastapi import APIRouter, Depends, HTTPException, Response

from ..config import get_settings
from ..database import db_cursor
from ..schemas import ImageUpload
from ..security import get_current_admin

try:
    from PIL import Image
except ImportError:  # pragma: no cover
    Image = None

router = APIRouter(tags=["images"])


@router.post("/images")
async def upload_image(payload: ImageUpload, _: str = Depends(get_current_admin)):
    if Image is None:
        raise HTTPException(status_code=500, detail="Image processing unavailable")
    settings = get_settings()

    raw = payload.data
    if "," in raw and raw.strip().startswith("data:"):
        raw = raw.split(",", 1)[1]
    try:
        blob = base64.b64decode(raw, validate=True)
    except (binascii.Error, ValueError):
        raise HTTPException(status_code=422, detail="Invalid base64 image data")
    if len(blob) > settings.max_image_bytes:
        raise HTTPException(status_code=413, detail="Image too large")

    try:
        img = Image.open(io.BytesIO(blob))
        img.verify()  # detect truncated/corrupt files
        img = Image.open(io.BytesIO(blob))  # reopen after verify
        img = img.convert("RGB")
    except Exception:
        raise HTTPException(status_code=422, detail="Unsupported or corrupt image")

    max_dim = settings.image_max_dimension
    if max(img.size) > max_dim:
        img.thumbnail((max_dim, max_dim), Image.LANCZOS)

    out = io.BytesIO()
    img.save(out, format="WEBP", quality=82, method=6)  # re-encode drops all metadata
    data = out.getvalue()

    with db_cursor(commit=True) as cur:
        cur.execute(
            "INSERT INTO images (mime, data, width, height, byte_size) VALUES (?, ?, ?, ?, ?)",
            ("image/webp", data, img.width, img.height, len(data)),
        )
        image_id = cur.lastrowid
    return {"id": image_id, "width": img.width, "height": img.height}


@router.get("/images/{image_id}")
async def get_image(image_id: int):
    with db_cursor() as cur:
        cur.execute("SELECT mime, data FROM images WHERE id = ?", (image_id,))
        row = cur.fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Image not found")
    return Response(
        content=row["data"],
        media_type=row["mime"],
        headers={"Cache-Control": "public, max-age=31536000, immutable"},
    )
