from app.agent.graph import create_hr_graph
from app.database import SessionLocal


def test_agent_graph_can_be_created():

    db = SessionLocal()

    try:
        graph = create_hr_graph(
            db,
            "EMP1001"
        )

        assert graph is not None

    finally:
        db.close()