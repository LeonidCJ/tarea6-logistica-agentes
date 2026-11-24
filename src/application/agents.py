from src.domain.models import (
    HIGH_VALUE_THRESHOLD_USD,
    IncidentType,
    LogisticsState,
    Severity,
    requires_human_review,
)
from src.infrastructure.mcp_tools import (
    mcp_check_warehouse_stock,
    mcp_draft_resolution_plan,
    mcp_execute_dispatch_update,
    mcp_get_shipment_status,
)


def logistics_triage_agent(state: LogisticsState) -> dict:
    """Agente 1: Analiza el reporte, consulta MCP y diagnostica severidad."""
    text = state["report"].lower()
    info = mcp_get_shipment_status(state["shipment_id"])

    if (
        any(k in text for k in ["roto", "dañado", "abierto", "mal estado"])
        or info["value_usd"] >= HIGH_VALUE_THRESHOLD_USD
    ):
        incident_type: IncidentType = "reemplazo"
        severity: Severity = "alta"
    elif any(k in text for k in ["retraso", "tarde", "demora", "no llega"]):
        incident_type = "reprogramacion"
        severity = "media" if info["delay_days"] >= 2 else "baja"
    else:
        incident_type = "consulta_estado"
        severity = "baja"

    stock = mcp_check_warehouse_stock(incident_type)
    diagnosis = (
        f"Estado={info['status']}, retraso={info['delay_days']}d, "
        f"valor=${info['value_usd']}, stock disponible={stock}."
    )
    return {
        "incident_type": incident_type,
        "severity": severity,
        "diagnosis": diagnosis,
    }


def resolution_agent(state: LogisticsState) -> dict:
    """Agente 2: Diseña la propuesta de solución y evalúa pausa HITL."""
    plan = mcp_draft_resolution_plan(
        state["shipment_id"], state["incident_type"], state["severity"]
    )
    needs_hitl = requires_human_review(state["severity"])

    if needs_hitl:
        msg = (
            f"Diagnóstico listo ({state['diagnosis']}). "
            "Se requiere aprobación de un supervisor antes de ejecutar la acción."
        )
    else:
        executed = mcp_execute_dispatch_update(plan)
        msg = f"Diagnóstico: {state['diagnosis']} | {executed}"

    return {
        "draft_plan": plan,
        "requires_hitl": needs_hitl,
        "final_response": msg,
    }
