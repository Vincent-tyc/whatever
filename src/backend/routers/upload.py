import os
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException
from src.backend.config import PRELOADED_TEXTS_DIR, UPLOAD_DIR
from src.backend.services.parser import parse_textbook

router = APIRouter(prefix="/api", tags=["upload"])

textbook_store: dict = {}


def preload_textbooks() -> int:
    if not os.path.isdir(PRELOADED_TEXTS_DIR):
        return 0

    loaded = 0
    for filename in sorted(os.listdir(PRELOADED_TEXTS_DIR)):
        if not filename.lower().endswith(".txt"):
            continue

        file_path = os.path.join(PRELOADED_TEXTS_DIR, filename)
        try:
            textbook = parse_textbook(file_path)
        except Exception as e:
            print(f"预加载教材失败 [{filename}]: {e}")
            continue

        if textbook.id not in textbook_store:
            textbook_store[textbook.id] = textbook
            loaded += 1

    return loaded


@router.post("/upload")
async def upload_textbook(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(400, "文件名不能为空")
    allowed = {".pdf", ".md", ".txt"}
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in allowed:
        raise HTTPException(400, f"不支持的格式: {ext}，仅支持 PDF/MD/TXT")

    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    textbook = parse_textbook(file_path)
    textbook_store[textbook.id] = textbook
    return textbook


@router.get("/textbooks")
async def list_textbooks():
    return list(textbook_store.values())


@router.get("/textbooks/{textbook_id}")
async def get_textbook(textbook_id: str):
    if textbook_id not in textbook_store:
        raise HTTPException(404, "教材不存在")
    return textbook_store[textbook_id]
