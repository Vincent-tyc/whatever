from dataclasses import dataclass
from math import ceil

from src.backend.models.schemas import Chapter, GraphData, TextbookDetail
from src.backend.services.extractor import extract_knowledge

graph_store: dict[str, GraphData] = {}
graph_progress_store: dict[str, int] = {}

SEGMENT_CHARS = 4000


@dataclass
class GraphBuildResult:
    graph: GraphData
    segment_index: int
    total_segments: int
    is_complete: bool
    segment_title: str
    added_nodes: int
    added_edges: int


def _total_chars(textbook: TextbookDetail) -> int:
    return sum(len(chapter.content) for chapter in textbook.chapters if len(chapter.content) >= 100)


def _segment_count(textbook: TextbookDetail) -> int:
    total = _total_chars(textbook)
    return max(1, ceil(total / SEGMENT_CHARS))


def _next_textbook_segment(textbook: TextbookDetail) -> tuple[Chapter, int, int]:
    total_segments = _segment_count(textbook)
    segment_index = graph_progress_store.get(textbook.id, 0)
    if segment_index >= total_segments:
        segment_index = total_segments - 1

    segment_start = segment_index * SEGMENT_CHARS
    remaining_start = segment_start

    for chapter in textbook.chapters:
        content = chapter.content
        if len(content) < 100:
            continue

        if remaining_start >= len(content):
            remaining_start -= len(content)
            continue

        sampled_content = content[remaining_start:remaining_start + SEGMENT_CHARS]
        sample_id = f"{chapter.chapter_id}_seg_{segment_index + 1:04d}"
        sample = Chapter(
            chapter_id=sample_id,
            title=f"{chapter.title} 片段 {segment_index + 1}/{total_segments}",
            page_start=chapter.page_start,
            page_end=chapter.page_end,
            content=sampled_content,
            char_count=len(sampled_content),
        )
        return sample, segment_index, total_segments

    raise ValueError("没有可用于建图的章节内容，章节文本可能为空或过短")


async def build_graph_for_textbook(textbook: TextbookDetail, progress_callback=None) -> GraphBuildResult:
    segment, segment_index, total_segments = _next_textbook_segment(textbook)
    if progress_callback:
        progress_callback(segment_index + 1, total_segments)

    try:
        nodes, relations = extract_knowledge(
            chapter_content=segment.content,
            chapter_title=segment.title,
            textbook_name=textbook.title,
            start_page=segment.page_start,
            textbook_id=f"{textbook.id}_{segment.chapter_id}",
        )
    except Exception as e:
        raise RuntimeError(f"建图失败：{segment.title}: {e}") from e

    if not nodes:
        raise RuntimeError("建图失败：模型没有返回可解析的知识点")

    existing_graph = graph_store.get(textbook.id, GraphData(nodes=[], edges=[]))
    existing_node_ids = {node.id for node in existing_graph.nodes}
    existing_edge_keys = {(edge.source, edge.target, edge.relation_type) for edge in existing_graph.edges}

    new_nodes = [node for node in nodes if node.id not in existing_node_ids]
    new_edges = [
        edge
        for edge in relations
        if (edge.source, edge.target, edge.relation_type) not in existing_edge_keys
    ]

    graph = GraphData(
        nodes=[*existing_graph.nodes, *new_nodes],
        edges=[*existing_graph.edges, *new_edges],
    )
    graph_store[textbook.id] = graph

    next_segment_index = segment_index + 1
    graph_progress_store[textbook.id] = min(next_segment_index, total_segments)

    return GraphBuildResult(
        graph=graph,
        segment_index=segment_index + 1,
        total_segments=total_segments,
        is_complete=next_segment_index >= total_segments,
        segment_title=segment.title,
        added_nodes=len(new_nodes),
        added_edges=len(new_edges),
    )


def get_graph(textbook_id: str) -> GraphData:
    return graph_store.get(textbook_id, GraphData(nodes=[], edges=[]))


def get_all_graphs() -> dict[str, GraphData]:
    return graph_store


def get_graph_progress(textbook_id: str, textbook: TextbookDetail | None = None) -> dict:
    total_segments = _segment_count(textbook) if textbook else 1
    next_segment = min(graph_progress_store.get(textbook_id, 0) + 1, total_segments)
    return {
        "textbook_id": textbook_id,
        "next_segment": next_segment,
        "total_segments": total_segments,
        "is_complete": graph_progress_store.get(textbook_id, 0) >= total_segments,
    }
