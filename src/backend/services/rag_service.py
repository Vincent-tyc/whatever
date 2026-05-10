import numpy as np
import faiss
from openai import OpenAI
from src.backend.config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL
from src.backend.services.embedder import encode_texts
from src.backend.routers.upload import textbook_store
from src.backend.models.schemas import RagChunk, RagAnswer, Citation

_client = None

def _get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)
    return _client

chunk_store: list[RagChunk] = []
faiss_index = None


def chunk_textbook(textbook_id: str):
    """将教材分块，500-800字/chunk，100字重叠"""
    global chunk_store
    textbook = textbook_store.get(textbook_id)
    if not textbook:
        return

    for chapter in textbook.chapters:
        text = chapter.content
        chunk_size = 600
        overlap = 100
        start = 0

        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunk_text = text[start:end]

            chunk_store.append(RagChunk(
                chunk_id=f"chunk_{textbook_id}_{len(chunk_store):05d}",
                textbook_name=textbook.title,
                chapter=chapter.title,
                page=chapter.page_start,
                content=chunk_text
            ))
            start = end - overlap if end < len(text) else len(text)


def build_faiss_index():
    """为所有chunk构建FAISS向量索引"""
    global faiss_index, chunk_store
    if not chunk_store:
        return

    texts = [c.content for c in chunk_store]
    embeddings = encode_texts(texts)

    dim = embeddings.shape[1]
    faiss_index = faiss.IndexFlatIP(dim)  # 内积相似度（归一化后等同余弦相似度）
    faiss_index.add(embeddings.astype(np.float32))


def search_chunks(query: str, top_k: int = 5) -> list[tuple[RagChunk, float]]:
    global faiss_index, chunk_store
    if faiss_index is None or not chunk_store:
        return []

    query_embedding = encode_texts([query])
    scores, indices = faiss_index.search(query_embedding.astype(np.float32), top_k)

    results = []
    for score, idx in zip(scores[0], indices[0]):
        if idx >= 0 and idx < len(chunk_store):
            results.append((chunk_store[idx], float(score)))
    return results


def generate_answer(question: str, chunks: list[tuple[RagChunk, float]]) -> RagAnswer:
    if not chunks:
        return RagAnswer(
            question=question,
            answer="当前知识库中未找到相关信息",
            citations=[],
            source_chunks=[]
        )

    context_parts = []
    citations = []
    seen = set()

    for chunk, score in chunks:
        context_parts.append(f"[来源：{chunk.textbook_name}，{chunk.chapter}，第{chunk.page}页]\n{chunk.content}")

        key = f"{chunk.textbook_name}:{chunk.chapter}"
        if key not in seen:
            citations.append(Citation(
                textbook=chunk.textbook_name,
                chapter=chunk.chapter,
                page=chunk.page,
                relevance_score=score
            ))
            seen.add(key)

    context = "\n\n---\n\n".join(context_parts)

    prompt = f"""你是学科知识整合助手。请仅基于以下教材内容回答用户问题。

## 约束
- 只基于提供的上下文回答，不要使用自身知识
- 每个回答附带来源引用，格式为 [教材名称, 第X章, 第X页]
- 如果上下文中找不到答案，回复"当前知识库中未找到相关信息"

## 上下文
{context}

## 用户问题
{question}

## 回答（含引用）"""

    response = _get_client().chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=1000
    )

    answer_text = response.choices[0].message.content

    return RagAnswer(
        question=question,
        answer=answer_text,
        citations=citations,
        source_chunks=[c.content[:200] for c, _ in chunks]
    )
