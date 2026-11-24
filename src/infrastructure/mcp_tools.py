from src.domain.models import IncidentType, Severity


def mcp_get_shipment_status(shipment_id: str) -> dict:
    """Simulación de Tool MCP para consultar estado de envío."""
    shipments = {
        "ENV-101": {"status": "retrasado", "delay_days": 3, "value_usd": 45},
        "ENV-202": {"status": "dañado", "delay_days": 0, "value_usd": 320},
        "ENV-303": {"status": "en_transito", "delay_days": 0, "value_usd": 50},
    }
    return shipments.get(
        shipment_id, {"status": "en_transito", "delay_days": 1, "value_usd": 60}
    )


def mcp_check_warehouse_stock(incident_type: IncidentType) -> int:
    """Simulación de Tool MCP para verificar stock en almacén."""
    return 15 if incident_type == "reemplazo" else 8


def mcp_draft_resolution_plan(
    shipment_id: str, incident_type: IncidentType, severity: Severity
) -> str:
    """Simulación de Tool MCP para redactar borrador de plan."""
    return (
        f"[BORRADOR PLAN] Envío={shipment_id} | "
        f"Acción={incident_type} | Severidad={severity}"
    )


def mcp_execute_dispatch_update(plan: str) -> str:
    """Simulación de Tool MCP para ejecutar la acción en el ERP de despacho."""
    return f"Plan ejecutado en sistema logístico: {plan}"
