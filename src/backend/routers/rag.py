from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from src.backend.services import rag_service
from src.backend.routers.upload import textbook_store

router = APIRouter(prefix="/api/rag", tags=["rag"])


class QueryRequest(BaseModel):
    question: str


@router.post("/index")
async def index_textbooks():
    if not textbook_store:
        raise HTTPException(400, "请先上传教材")

    try:
        for tid in textbook_store:
            rag_service.chunk_textbook(tid)

        backend = rag_service.build_faiss_index()
    except Exception as e:
        raise HTTPException(500, f"RAG索引建立失败：{e}") from e

    return {"status": "indexed", "total_chunks": len(rag_service.chunk_store), "embedding": backend}


@router.post("/query")
async def query_rag(req: QueryRequest):
    chunks = rag_service.search_chunks(req.question, top_k=5)
    result = rag_service.generate_answer(req.question, chunks)
    return result


@router.get("/status")
async def rag_status():
    return {
        "indexed_textbooks": len(textbook_store),
        "total_chunks": len(rag_service.chunk_store),
        "has_index": rag_service.faiss_index is not None
    }
