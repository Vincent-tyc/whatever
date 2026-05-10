from fastapi import APIRouter, HTTPException
from src.backend.routers.upload import textbook_store
from src.backend.services.graph_builder import build_graph_for_textbook, get_graph, get_all_graphs

router = APIRouter(prefix="/api/graph", tags=["graph"])

build_status: dict[str, str] = {}


@router.post("/build/{textbook_id}")
async def build_graph(textbook_id: str):
    if textbook_id not in textbook_store:
        raise HTTPException(404, "教材不存在")

    build_status[textbook_id] = "building"
    textbook = textbook_store[textbook_id]
    await build_graph_for_textbook(textbook)
    build_status[textbook_id] = "done"

    return {"status": "done", "textbook_id": textbook_id}


@router.get("/data/{textbook_id}")
async def get_graph_data(textbook_id: str):
    graph = get_graph(textbook_id)
    return graph


@router.get("/data")
async def get_merged_graph_data():
    """返回所有教材的合并图谱数据（前端可视化用）"""
    all_graphs = get_all_graphs()
    all_nodes = []
    all_edges = []

    colors = ["#ff6b6b", "#4ecdc4", "#ffe66d", "#a29bfe", "#fd79a8",
              "#00cec9", "#fab1a0"]

    color_idx = 0
    for textbook_id, graph in all_graphs.items():
        textbook = textbook_store.get(textbook_id)
        textbook_name = textbook.title if textbook else textbook_id

        for node in graph.nodes:
            node.color = colors[color_idx % len(colors)]
            all_nodes.append(node)

        all_edges.extend(graph.edges)
        color_idx += 1

    return {"nodes": [n.model_dump() for n in all_nodes], "edges": [e.model_dump() for e in all_edges]}


@router.get("/build-status/{textbook_id}")
async def get_build_status(textbook_id: str):
    return {"textbook_id": textbook_id, "status": build_status.get(textbook_id, "not_started")}
