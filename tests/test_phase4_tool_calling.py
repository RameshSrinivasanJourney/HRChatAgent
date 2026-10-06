from app.agent.graph import create_hr_graph
from app.database import SessionLocal


def test_agent_can_answer_employee_leave_balance():
    db = SessionLocal()

    try:
        graph = create_hr_graph(
            db,
            "EMP1001",
        )

        result = graph.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": "How much CL do I have?",
                    }
                ],
                "employee_id": "EMP1001",
            }
        )

        final_message = result["messages"][-1]

        print("\nAgent response:")
        print(final_message.content)

        assert final_message.content
        assert "7" in final_message.content

    finally:
        db.close()