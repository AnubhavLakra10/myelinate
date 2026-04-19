"""Data models for myelinate."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class Confidence(str, Enum):
    """How certain we are about a relationship."""

    EXTRACTED = "EXTRACTED"
    INFERRED = "INFERRED"
    AMBIGUOUS = "AMBIGUOUS"


class Node(BaseModel):
    """A concept in the knowledge graph."""

    id: str
    label: str
    source_file: str
    source_location: str = ""
    node_type: str = "concept"


class Edge(BaseModel):
    """A relationship between two concepts."""

    source: str
    target: str
    relation: str
    confidence: Confidence = Confidence.EXTRACTED
    weight: float = 1.0


class Extraction(BaseModel):
    """Result of extracting concepts from a single file."""

    source_file: str
    nodes: list[Node] = Field(default_factory=list)
    edges: list[Edge] = Field(default_factory=list)


class ReviewCard(BaseModel):
    """A spaced repetition card generated from a graph edge."""

    card_id: str
    question: str
    answer: str
    source_edge: str
    difficulty: float = 0.3
    stability: float = 1.0
    due: float = 0.0
    reps: int = 0
    lapses: int = 0
    state: int = 0
