"""Explicit Astra tool architecture: orchestration may choose tools, tools own calculations."""

from dataclasses import dataclass
from typing import Callable

from app.domain.calculations import calculate_css, hr_zones, readiness_score, session_rpe_load
from app.domain.workout_engine import generate_workout


@dataclass(frozen=True)
class AstraTool:
    name: str
    description: str
    handler: Callable[..., object]
    deterministic: bool = True


ASTRA_TOOLS = {
    tool.name: tool
    for tool in (
        AstraTool("athlete_context", "Validated athlete profile and consent scope.", lambda **context: context),
        AstraTool("performance", "Date-based performance records and trend comparison.", lambda records: records),
        AstraTool("workout", "Feasibility-aware workout generator.", generate_workout),
        AstraTool("css_calculator", "200/400 CSS calculation; not an exact lactate threshold.", calculate_css),
        AstraTool("hr_zone_calculator", "Heart-rate zones from measured HRmax/resting HR.", hr_zones),
        AstraTool("training_load", "Session RPE load calculation.", session_rpe_load),
        AstraTool("readiness", "Explainable multi-signal readiness score.", readiness_score),
        AstraTool("race_analysis", "Expected versus actual race metrics.", lambda expected, actual: {"expected": expected, "actual": actual}),
        AstraTool("knowledge_retrieval", "Retrieves article context and related evidence.", lambda articles: articles),
        AstraTool("research", "Evidence pipeline boundary; source fetching remains explicit.", lambda question: {"question": question, "sources": []}),
        AstraTool("technique", "Evidence-labeled technique issue context.", lambda issue: issue),
        AstraTool("plan_generator", "Versioned plan orchestration boundary.", lambda inputs: {"inputs": inputs, "version": "v1"}),
    )
}
