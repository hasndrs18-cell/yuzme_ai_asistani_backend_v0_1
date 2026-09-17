from typing import Literal, Sequence

from langgraph.graph import END

from app.agent.prompts import PromptContext, build_system_prompt
from app.agent.schemas import ConversationMode, Decision, DecisionType, IntentResult, SafetyState
from app.agent.state import AgentState
from app.agent.tools import SWIMMING_TOOLS
from app.integrations.llm import LLMClient
from app.integrations.research import ResearchProvider, ResearchResult
from app.memory.context_builder import ContextBuilder


class AgentNodes:
    def __init__(self, context_builder: ContextBuilder, llm: LLMClient, tools: Sequence = SWIMMING_TOOLS, research: ResearchProvider | None = None) -> None:
        self.context_builder = context_builder
        self.llm = llm
        self.tools = tuple(tools)
        self.research = research

    async def load_context(self, state: AgentState) -> dict:
        context = await self.context_builder.build(
            student_id=state["student_id"],
            user_message=state["user_message"],
        )
        return {"student_context": context}

    async def safety_check(self, state: AgentState) -> dict:
        text = state["user_message"].lower()
        safety_terms = ("şiddetli ağrı", "bayılma", "nefes alamıyorum", "yaralandım")
        needs_escalation = any(term in text for term in safety_terms)
        result = {
            "safety": SafetyState(
                safe_to_continue=not needs_escalation,
                needs_escalation=needs_escalation,
                reason="Fiziksel güvenlik açısından profesyonel değerlendirme gerekebilir."
                if needs_escalation
                else None,
            )
        }
        if needs_escalation:
            result["mode"] = ConversationMode.COACH_ESCALATION
        return result

    async def classify_intent(self, state: AgentState) -> dict:
        text = state["user_message"].lower()
        if any(x in text for x in ("bugün ne", "antrenman yap", "çalışmalıyım")):
            intent = "TRAINING_REQUEST"
        elif any(x in text for x in ("neden", "nasıl", "nedir", "ne demek")):
            intent = "QUICK_QUESTION"
        elif any(x in text for x in ("bırak", "yapamıyorum", "pes")):
            intent = "MOTIVATION"
        elif any(x in text for x in ("program", "hafta", "plan")):
            intent = "PROGRAM_REQUEST"
        else:
            intent = "GENERAL_ASSISTANCE"
        return {"intent": IntentResult(intent=intent, confidence=0.9)}

    async def select_mode(self, state: AgentState) -> dict:
        intent = state["intent"].intent
        if not state["safety"].safe_to_continue:
            mode = ConversationMode.COACH_ESCALATION
        elif intent == "TRAINING_REQUEST":
            mode = ConversationMode.DAILY_CHECKIN
        elif intent == "MOTIVATION":
            mode = ConversationMode.MOTIVATION_MODE
        elif intent == "PROGRAM_REQUEST":
            mode = ConversationMode.STRATEGY_MODE
        else:
            mode = ConversationMode.QA_MODE
        return {"mode": mode}

    async def build_decision(self, state: AgentState) -> dict:
        if not state["safety"].safe_to_continue:
            decision = Decision(
                type=DecisionType.ESCALATE_TO_COACH,
                reason=state["safety"].reason or "Profesyonel değerlendirme gerekiyor.",
                confidence="high",
                next_action="Antrenör veya uygun yetişkin/profesyonel değerlendirmesi",
            )
        else:
            intent = state["intent"].intent
            mapping = {
                "TRAINING_REQUEST": DecisionType.ASSIGN_SESSION,
                "MOTIVATION": DecisionType.MOTIVATE,
                "PROGRAM_REQUEST": DecisionType.ADJUST_PROGRAM,
                "QUICK_QUESTION": DecisionType.ANSWER,
                "GENERAL_ASSISTANCE": DecisionType.ASK,
            }
            decision_type = mapping.get(intent, DecisionType.ASK)
            decision = Decision(
                type=decision_type,
                reason=f"Niyet: {intent}",
                confidence="medium",
                next_action="Öğrenci bağlamına göre yanıt oluştur",
            )
        return {"decision": decision}

    async def generate_response(self, state: AgentState) -> dict:
        context = PromptContext(student=state["student_context"], mode=state["mode"])
        research_result = ResearchResult(question=state["user_message"], sources=(), confidence="LOW", contradiction_detected=False, limitation="Araştırma yapılmadı.")
        if self.research is not None:
            try:
                research_result = await self.research.search(state["user_message"])
            except Exception:
                research_result = ResearchResult(question=state["user_message"], sources=(), confidence="LOW", contradiction_detected=False, limitation="Araştırma sağlayıcısına ulaşılamadı.")
        research_context = "\n".join(
            f"[{index}] {source.title} | {source.url}\nBulgu: {source.finding}"
            for index, source in enumerate(research_result.sources, start=1)
        )
        prompt = build_system_prompt(context, tuple(tool.name for tool in self.tools), research_context)
        if state["decision"].type is DecisionType.ESCALATE_TO_COACH:
            response = "Burada kendi başıma kesin yönlendirme yapmak doğru olmaz. Antrenörünle veya uygun bir yetişkin/profesyonelle değerlendirelim."
        else:
            try:
                response = await self.llm.generate(prompt, state["user_message"])
            except Exception:
                response = "AI sağlayıcısına şu anda ulaşılamıyor. Yanlış yönlendirme yapmamak için bu soruya tahminle cevap vermiyorum; lütfen biraz sonra tekrar deneyin."
        return {"response": response}



def route_after_safety(state: AgentState) -> Literal["classify_intent", "build_decision"]:
    return "classify_intent" if state["safety"].safe_to_continue else "build_decision"


def finish(_: AgentState) -> str:
    return END
