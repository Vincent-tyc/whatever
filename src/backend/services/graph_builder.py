from src.backend.services.extractor import extract_knowledge
from src.backend.models.schemas import TextbookDetail, KnowledgeNode, Relation, GraphData

graph_store: dict[str, GraphData] = {}


async def build_graph_for_textbook(textbook: TextbookDetail, progress_callback=None) -> GraphData:
    all_nodes = []
    all_relations = []

    for i, chapter in enumerate(textbook.chapters):
        if progress_callback:
            progress_callback(i + 1, len(textbook.chapters))

        if len(chapter.content) < 100:
            continue

        nodes, relations = extract_knowledge(
            chapter_content=chapter.content,
            chapter_title=chapter.title,
            textbook_name=textbook.title,
            start_page=chapter.page_start,
            textbook_id=textbook.id
        )
        all_nodes.extend(nodes)
        all_relations.extend(relations)

    graph = GraphData(nodes=all_nodes, edges=all_relations)
    graph_store[textbook.id] = graph
    return graph


def get_graph(textbook_id: str) -> GraphData:
    return graph_store.get(textbook_id, GraphData(nodes=[], edges=[]))


def get_all_graphs() -> dict[str, GraphData]:
    return graph_store
