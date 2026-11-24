from typing import Literal

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import interrupt

from src.application.agents import logistics_triage_agent, resolution_agent
from src.domain.models import LogisticsState
from src.infrastructure.mcp_tools import mcp_execute_dispatch_update


def route_after_resolution(state: LogisticsState) -> Literal["hitl_review", "__end__"]:
    """Transición condicional hacia HITL o finalización."""
    return "hitl_review" if state["requires_hitl"] else END


def hitl_review(state: LogisticsState) -> dict:
    """Nodo HITL: Interrumpe el flujo esperando input humano externo."""
    decision = interrupt(
        {
            "reason": "Validación humana por severidad alta o impacto en inventario/valor.",
            "shipment_id": state["shipment_id"],
            "diagnosis": state["diagnosis"],
            "draft_plan": state["draft_plan"],
        }
    )

    if decision == "aprobar":
        out = mcp_execute_dispatch_update(state["draft_plan"])
        final = f"{state['final_response']} -> {out}"
    else:
        final = (
            f"{state['final_response']} -> "
            "Caso enviado a revisión manual del supervisor."
        )

    return {
        "hitl_decision": str(decision),
        "final_response": final,
    }


def build_logistics_graph():
    """Ensamblado del StateGraph de LangGraph."""
    builder = StateGraph(LogisticsState)
    builder.add_node("logistics_triage_agent", logistics_triage_agent)
    builder.add_node("resolution_agent", resolution_agent)
    builder.add_node("hitl_review", hitl_review)

    builder.add_edge(START, "logistics_triage_agent")
    builder.add_edge("logistics_triage_agent", "resolution_agent")
    builder.add_conditional_edges("resolution_agent", route_after_resolution)
    builder.add_edge("hitl_review", END)

    return builder.compile(checkpointer=InMemorySaver())
