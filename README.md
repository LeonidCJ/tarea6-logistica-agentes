# Tarea 6 — Sistema Agéntico Multiagente para Logística

Prototipo en **LangGraph** con dos agentes (Diagnóstico y Resolución), tools MCP simuladas,
memoria de corto plazo (`InMemorySaver` + `thread_id`) y un punto **HITL** (`interrupt()`)
para incidencias de severidad alta (daño físico o valor ≥ $200).

## Estructura (Clean Architecture)

```text
src/
├── domain/models.py            # Estado, tipos y reglas de negocio puras
├── infrastructure/mcp_tools.py # Adaptadores MCP (simulados)
├── application/agents.py       # Agente 1 (triage) y Agente 2 (resolución)
├── graph/workflow.py           # StateGraph, memoria y nodo HITL
├── presentation/web_app.py     # API FastAPI + interfaz web (GET /)
└── main.py                     # Demo ejecutable
tests/test_pyramid.py           # 10 pruebas: 5 típicas, 3 borde, 2 confrontación
```

## Instalación

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Ejecución

```powershell
python -m src.main      # Demo con interrupción HITL y reanudación
python -m pytest -v     # Pirámide de pruebas

# Servidor web local
uvicorn src.presentation.web_app:app --reload --port 8000

# Despliegue (Render)
uvicorn src.presentation.web_app:app --host 0.0.0.0 --port $PORT
```

## Flujo

1. `logistics_triage_agent` consulta `mcp_get_shipment_status` y `mcp_check_warehouse_stock`,
   clasifica la incidencia y asigna severidad.
2. `resolution_agent` genera el plan con `mcp_draft_resolution_plan`.
   - Severidad baja/media → ejecuta `mcp_execute_dispatch_update` de forma autónoma.
   - Severidad alta → el grafo pasa a `hitl_review`, que se congela con `interrupt()`.
3. El supervisor reanuda con `Command(resume="aprobar")` o `Command(resume="rechazar")`.
