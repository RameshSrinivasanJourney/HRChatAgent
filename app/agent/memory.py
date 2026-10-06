from uuid import uuid4

from sqlalchemy.orm import Session

from app.models import Conversation, ConversationMessage


class ConversationMemory:

    def __init__(
        self,
        db: Session,
        employee_id: str,
    ):
        self.db = db
        self.employee_id = employee_id

    def create_conversation(self) -> str:

        conversation_id = str(uuid4())

        conversation = Conversation(
            conversation_id=conversation_id,
            employee_id=self.employee_id,
        )

        self.db.add(conversation)
        self.db.commit()

        return conversation_id

    def get_or_create_conversation(
        self,
        conversation_id: str | None = None,
    ) -> str:

        if conversation_id:

            conversation = (
                self.db.query(Conversation)
                .filter(
                    Conversation.conversation_id
                    == conversation_id,
                    Conversation.employee_id
                    == self.employee_id,
                )
                .first()
            )

            if conversation is None:
                raise ValueError(
                    "Conversation not found for authenticated employee."
                )

            return conversation_id

        return self.create_conversation()

    def save_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
    ):

        message = ConversationMessage(
            conversation_id=conversation_id,
            role=role,
            content=content,
        )

        self.db.add(message)
        self.db.commit()

    def get_messages(
        self,
        conversation_id: str,
    ) -> list[dict]:

        messages = (
            self.db.query(ConversationMessage)
            .filter(
                ConversationMessage.conversation_id
                == conversation_id
            )
            .order_by(ConversationMessage.id)
            .all()
        )

        return [
            {
                "role": message.role,
                "content": message.content,
            }
            for message in messages
        ]