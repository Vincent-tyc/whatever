import json
import re
from openai import OpenAI
from src.backend.config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL
from src.backend.models.schemas import KnowledgeNode, Relation, RelationType

_client = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)
    return _client


EXTRACT_PROMPT = """你是一位医学教育专家。请从以下教材章节内容中提取核心知识点，并识别它们之间的关系。

## 要求
1. 输出严格的JSON格式，不要输出任何其他文字
2. 每个知识点需要：name(名称)、definition(一句话定义)、category(类别：核心概念/定理/方法/现象)
3. 识别知识点之间的关系类型：
   - prerequisite(前置依赖)：学B前必须先掌握A
   - parallel(并列关系)：同一层级的平行概念
   - contains(包含关系)：上位概念包含下位概念
   - applies_to(应用关系)：某知识点是另一个的应用场景
4. 每个关系需要source和target的name（与节点name对应），以及简短描述

## 章节内容
{content}

## 输出格式
{{
  "nodes": [
    {{"name": "知识点名称", "definition": "一句话定义", "category": "核心概念"}}
  ],
  "relations": [
    {{"source": "知识点A", "target": "知识点B", "relation_type": "prerequisite", "description": "说明"}}
  ]
}}
"""


def extract_knowledge(chapter_content: str, chapter_title: str, textbook_name: str,
                      start_page: int, textbook_id: str) -> tuple[list[KnowledgeNode], list[Relation]]:
    prompt = EXTRACT_PROMPT.format(content=chapter_content[:4000])

    response = _get_client().chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=3000
    )

    result_text = response.choices[0].message.content
    result_text = result_text.replace("```json", "").replace("```", "").strip()

    try:
        data = json.loads(result_text)
    except json.JSONDecodeError:
        match = re.search(r'\{[\s\S]*\}', result_text)
        if match:
            data = json.loads(match.group(0))
        else:
            return [], []

    nodes = []
    relations = []
    node_name_to_id = {}

    for i, node_data in enumerate(data.get("nodes", [])):
        node_id = f"{textbook_id}_node_{i+1:03d}"
        node_name_to_id[node_data["name"]] = node_id
        nodes.append(KnowledgeNode(
            id=node_id,
            name=node_data["name"],
            definition=node_data.get("definition", ""),
            category=node_data.get("category", "核心概念"),
            chapter=chapter_title,
            page=start_page,
            textbook_id=textbook_id,
            textbook_name=textbook_name
        ))

    for rel_data in data.get("relations", []):
        source_id = node_name_to_id.get(rel_data["source"])
        target_id = node_name_to_id.get(rel_data["target"])
        if source_id and target_id:
            relations.append(Relation(
                source=source_id,
                target=target_id,
                relation_type=rel_data.get("relation_type", "parallel"),
                description=rel_data.get("description", "")
            ))

    return nodes, relations
