from app.agent.service import HRChatService
from app.database import SessionLocal
from app.models import ConversationMessage


def test_phase5_multi_turn_conversation():

    db = SessionLocal()

    try:

        service = HRChatService(
            db,
            "EMP1001",
        )

        # -------------------------------------------------
        # Turn 1
        # -------------------------------------------------

        conversation_id = service.create_conversation()

        print("\n========================================")
        print("CONVERSATION CREATED")
        print("========================================")
        print(f"Conversation ID: {conversation_id}")

        response1 = service.chat(
            conversation_id,
            "How much EL do I have?",
        )

        print("\nUser:")
        print("How much EL do I have?")

        print("\nAgent:")
        print(response1)

        assert response1
        assert "14" in response1

        # -------------------------------------------------
        # Turn 2
        # -------------------------------------------------

        response2 = service.chat(
            conversation_id,
            "If I take 5 days, how much will remain?",
        )

        print("\n----------------------------------------")
        print("TURN 2")
        print("----------------------------------------")

        print("\nUser:")
        print("If I take 5 days, how much will remain?")

        print("\nAgent:")
        print(response2)

        assert response2
        assert "9" in response2

        # -------------------------------------------------
        # Verify database memory
        # -------------------------------------------------

        messages = (
            db.query(ConversationMessage)
            .filter(
                ConversationMessage.conversation_id
                == conversation_id
            )
            .order_by(ConversationMessage.id)
            .all()
        )

        print("\n========================================")
        print("STORED CONVERSATION")
        print("========================================")

        for message in messages:

            print(
                f"{message.role.upper()}: "
                f"{message.content}"
            )

        assert len(messages) == 4

        assert messages[0].role == "user"
        assert messages[1].role == "assistant"
        assert messages[2].role == "user"
        assert messages[3].role == "assistant"

    finally:

        db.close()