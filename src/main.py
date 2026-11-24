from langgraph.types import Command

from src.graph.workflow import build_logistics_graph


def run_demo():
    app = build_logistics_graph()
    cfg = {"configurable": {"thread_id": "log-001"}}

    print("--- 1. Ejecutando caso con interrupción HITL ---")
    result = app.invoke(
        {
            "shipment_id": "ENV-202",
            "report": "El paquete llegó con la caja rota y el equipo golpeado.",
            "hitl_decision": None,
        },
        config=cfg,
    )
    print("Respuesta preliminar (Pausado en HITL):", result.get("final_response"))

    if "__interrupt__" in result:
        print("\n--- 2. Reanudando grafo con aprobación humana (Command resume) ---")
        resumed = app.invoke(Command(resume="aprobar"), config=cfg)
        print("Respuesta final post-HITL:", resumed.get("final_response"))


if __name__ == "__main__":
    run_demo()
