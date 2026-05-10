from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class ParseStatus(str, Enum):
    PENDING = "pending"
    PARSING = "parsing"
    DONE = "done"
    FAILED = "failed"


class TextbookInfo(BaseModel):
    id: str
    filename: str
    title: str
    format: str
    size_bytes: int
    status: ParseStatus = ParseStatus.PENDING
    total_pages: int = 0
    total_chars: int = 0


class Chapter(BaseModel):
    chapter_id: str
    title: str
    page_start: int
    page_end: int
    content: str
    char_count: int


class TextbookDetail(TextbookInfo):
    chapters: list[Chapter] = []


class KnowledgeNode(BaseModel):
    id: str
    name: str
    definition: str
    category: str
    chapter: str
    page: int
    textbook_id: str
    textbook_name: str
    frequency: int = 1
    color: str = "#ff6b6b"


class RelationType(str, Enum):
    PREREQUISITE = "prerequisite"
    PARALLEL = "parallel"
    CONTAINS = "contains"
    APPLIES_TO = "applies_to"


class Relation(BaseModel):
    source: str
    target: str
    relation_type: RelationType
    description: str


class GraphData(BaseModel):
    nodes: list[KnowledgeNode]
    edges: list[Relation]


class IntegrationDecision(BaseModel):
    decision_id: str
    action: str  # merge / keep / remove
    affected_nodes: list[str]
    result_name: str
    reason: str
    confidence: float


class IntegrationResult(BaseModel):
    original_total_chars: int
    merged_total_chars: int
    compression_ratio: float
    decisions: list[IntegrationDecision]
    merged_graph: GraphData


class RagChunk(BaseModel):
    chunk_id: str
    textbook_name: str
    chapter: str
    page: int
    content: str


class Citation(BaseModel):
    textbook: str
    chapter: str
    page: int
    relevance_score: float


class RagAnswer(BaseModel):
    question: str
    answer: str
    citations: list[Citation]
    source_chunks: list[str]


class DialogueMessage(BaseModel):
    role: str  # user / assistant
    content: str


class DialogueRequest(BaseModel):
    message: str
    history: list[DialogueMessage] = []


class DialogueResponse(BaseModel):
    reply: str
    history: list[DialogueMessage]
    decision_updates: list[IntegrationDecision] = []
