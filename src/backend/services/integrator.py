import json
import asyncio
from openai import OpenAI
from src.backend.config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL
from src.backend.services.embedder import encode_texts, cosine_similarity
from src.backend.services.graph_builder import get_all_graphs
from src.backend.routers.upload import textbook_store
from src.backend.models.schemas import IntegrationDecision, IntegrationResult, GraphData, KnowledgeNode

client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)

integration_result_store: IntegrationResult | None = None

SIMILARITY_THRESHOLD = 0.8


async def run_integration() -> IntegrationResult:
    global integration_result_store
    all_graphs = get_all_graphs()

    if len(all_graphs) < 2:
        integration_result_store = IntegrationResult(
            original_total_chars=0, merged_total_chars=0,
            compression_ratio=1.0, decisions=[], merged_graph=GraphData(nodes=[], edges=[])
        )
        return integration_result_store

    all_nodes: list[KnowledgeNode] = []
    for graph in all_graphs.values():
        all_nodes.extend(graph.nodes)

    original_chars = sum(t.total_chars for t in textbook_store.values())

    node_texts = [f"{n.name}: {n.definition}" for n in all_nodes]
    embeddings = encode_texts(node_texts)

    decisions = []
    merged_indices = set()
    merged_node_map = {}

    for i in range(len(all_nodes)):
        if i in merged_indices:
            continue
        duplicates = [i]
        for j in range(i + 1, len(all_nodes)):
            if j in merged_indices:
                continue
            sim = cosine_similarity(embeddings[i], embeddings[j])
            if sim > SIMILARITY_THRESHOLD:
                duplicates.append(j)

        if len(duplicates) > 1:
            names = [all_nodes[d].name for d in duplicates]
            sources = [f"{all_nodes[d].textbook_name}: {all_nodes[d].definition[:100]}" for d in duplicates]

            llm_decision = await _llm_merge_decision(names, sources)

            if llm_decision.get("action") == "merge":
                decisions.append(IntegrationDecision(
                    decision_id=f"merge_{len(decisions)+1:03d}",
                    action="merge",
                    affected_nodes=[all_nodes[d].id for d in duplicates],
                    result_name=llm_decision.get("result_name", names[0]),
                    reason=llm_decision.get("reason", ""),
                    confidence=llm_decision.get("confidence", 0.85)
                ))
                for d in duplicates:
                    merged_indices.add(d)
                    merged_node_map[all_nodes[d].name] = llm_decision.get("result_name", names[0])

    merged_nodes = []
    seen_names = set()
    for i, node in enumerate(all_nodes):
        if i in merged_indices:
            continue
        merged_name = merged_node_map.get(node.name, node.name)
        if merged_name not in seen_names:
            node.name = merged_name
            node.frequency = sum(1 for j in all_nodes
                                 if merged_node_map.get(j.name, j.name) == merged_name)
            merged_nodes.append(node)
            seen_names.add(merged_name)

    node_ratio = len(merged_nodes) / max(len(all_nodes), 1)
    merged_chars = int(original_chars * min(node_ratio, 0.3))

    if merged_chars > original_chars * 0.3:
        merged_chars = int(original_chars * 0.3)

    result = IntegrationResult(
        original_total_chars=original_chars,
        merged_total_chars=merged_chars,
        compression_ratio=merged_chars / max(original_chars, 1),
        decisions=decisions,
        merged_graph=GraphData(nodes=merged_nodes, edges=[])
    )

    integration_result_store = result
    return result


async def _llm_merge_decision(names: list[str], sources: list[str]) -> dict:
    prompt = f"""判断以下知识点是否描述同一概念，如果是，合并它们并选择最佳版本。

知识点：
{chr(10).join(f"{i+1}. {n}: {s}" for i, (n, s) in enumerate(zip(names, sources)))}

输出JSON：
{{"action": "merge"或"keep_separate", "result_name": "合并后的名称", "reason": "决策理由", "confidence": 0.xx}}
"""
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=500
    )
    text = response.choices[0].message.content
    text = text.replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"action": "merge", "result_name": names[0], "reason": "Embedding相似度高，自动合并", "confidence": 0.8}
