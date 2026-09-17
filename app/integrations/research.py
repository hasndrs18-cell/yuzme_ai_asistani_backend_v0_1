from dataclasses import dataclass
from enum import Enum


class EvidenceLevel(str, Enum):
    SYSTEMATIC_REVIEW = "SYSTEMATIC_REVIEW"
    META_ANALYSIS = "META_ANALYSIS"
    CONSENSUS = "CONSENSUS"
    PEER_REVIEWED = "PEER_REVIEWED"
    FEDERATION = "FEDERATION"
    EXPERT = "EXPERT"
    GENERAL = "GENERAL"


@dataclass(frozen=True)
class ResearchSource:
    title: str
    authors: str
    year: int
    publication: str
    url: str | None
    doi: str | None
    evidence_level: EvidenceLevel
    finding: str
    stance: str


@dataclass(frozen=True)
class ResearchResult:
    question: str
    sources: tuple[ResearchSource, ...]
    confidence: str
    contradiction_detected: bool
    limitation: str


class ResearchProvider:
    async def search(self, question: str) -> ResearchResult:
        raise NotImplementedError


class UnconfiguredResearchProvider(ResearchProvider):
    async def search(self, question: str) -> ResearchResult:
        return ResearchResult(question=question, sources=(), confidence="LOW", contradiction_detected=False, limitation="Research provider yapılandırılmamış; kaynak uydurulmadı.")
