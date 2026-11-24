from typing import Literal, TypedDict

IncidentType = Literal["reemplazo", "reprogramacion", "consulta_estado"]
Severity = Literal["baja", "media", "alta"]

HIGH_VALUE_THRESHOLD_USD = 200


class LogisticsState(TypedDict):
    shipment_id: str
    report: str
    incident_type: IncidentType
    severity: Severity
    diagnosis: str
    draft_plan: str
    requires_hitl: bool
    hitl_decision: str | None
    final_response: str


def requires_human_review(severity: Severity) -> bool:
    """Regla de dominio pura para determinar si un incidente requiere revisión humana."""
    return severity == "alta"
