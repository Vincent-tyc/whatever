from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="学科知识整合智能体", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health():
    return {"status": "ok", "message": "学科知识整合智能体运行中"}


# 后续任务注册路由
from src.backend.routers import upload
app.include_router(upload.router)
# from src.backend.routers import graph, integration, rag, dialogue
# app.include_router(graph.router)
# app.include_router(integration.router)
# app.include_router(rag.router)
# app.include_router(dialogue.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.backend.main:app", host="0.0.0.0", port=8000, reload=True)
