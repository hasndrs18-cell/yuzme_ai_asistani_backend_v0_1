from dataclasses import dataclass
from enum import Enum

import httpx


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


class TavilyResearchProvider(ResearchProvider):
    """Fast web search adapter; the model must cite these results and state limits."""

    def __init__(self, api_key: str, timeout_seconds: float = 4.0, max_results: int = 5) -> None:
        self.api_key = api_key
        self.timeout_seconds = timeout_seconds
        self.max_results = max_results

    async def search(self, question: str) -> ResearchResult:
        payload = {
            "api_key": self.api_key,
            "query": f"{question} swimming sports science World Aquatics peer reviewed",
            "search_depth": "advanced",
            "max_results": self.max_results,
            "include_answer": False,
            "include_raw_content": False,
        }
        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            response = await client.post("https://api.tavily.com/search", json=payload)
            response.raise_for_status()
        results = response.json().get("results", [])
        sources = tuple(
            ResearchSource(
                title=str(item.get("title", "Başlıksız kaynak")),
                authors="",
                year=0,
                publication=str(item.get("url", "Web")),
                url=item.get("url"),
                doi=None,
                evidence_level=EvidenceLevel.GENERAL,
                finding=str(item.get("content", ""))[:1200],
                stance="search_result",
            )
            for item in results
            if item.get("url") and item.get("content")
        )
        return ResearchResult(
            question=question,
            sources=sources,
            confidence="MEDIUM" if sources else "LOW",
            contradiction_detected=False,
            limitation="Web araması kaynak keşfi sağlar; klinik veya antrenör onayı yerine geçmez.",
        )
