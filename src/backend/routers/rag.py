from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from src.backend.services.rag_service import chunk_textbook, build_faiss_index, search_chunks, generate_answer, chunk_store, faiss_index
from src.backend.routers.upload import textbook_store

router = APIRouter(prefix="/api/rag", tags=["rag"])


class QueryRequest(BaseModel):
    question: str


@router.post("/index")
async def index_textbooks():
    if not textbook_store:
        raise HTTPException(400, "请先上传教材")

    for tid in textbook_store:
        chunk_textbook(tid)

    build_faiss_index()
    return {"status": "indexed", "total_chunks": len(chunk_store)}


@router.post("/query")
async def query_rag(req: QueryRequest):
    chunks = search_chunks(req.question, top_k=5)
    result = generate_answer(req.question, chunks)
    return result


@router.get("/status")
async def rag_status():
    return {
        "indexed_textbooks": len(textbook_store),
        "total_chunks": len(chunk_store),
        "has_index": faiss_index is not None
    }
