import time

from sqlalchemy.orm import Session
from langchain_core.messages import HumanMessage, AIMessage

from app.agent.audit import record_audit_event
from app.agent.graph import create_hr_graph
from app.agent.memory import ConversationMemory


class HRChatService:

    def __init__(
        self,
        db: Session,
        employee_id: str,
        correlation_id: str = "unknown",
    ):
        self.db = db
        self.employee_id = employee_id
        self.correlation_id = correlation_id

        self.memory = ConversationMemory(
            db,
            employee_id,
        )

    # =========================================================
    # CREATE CONVERSATION
    # =========================================================

    def create_conversation(self) -> str:
        """
        Create a new conversation for the authenticated employee.
        """

        return self.memory.create_conversation()

    # =========================================================
    # CHAT
    # =========================================================

    def chat(
        self,
        conversation_id: str,
        message: str,
    ) -> str:
        """
        Process an HR chat request.

        Flow:

            Validate conversation
                    ↓
            Save user message
                    ↓
            Load conversation history
                    ↓
            AGENT_STARTED
                    ↓
            LangGraph
                    ↓
            Tool execution
                    ↓
            AGENT_COMPLETED
                    ↓
            Save assistant response
        """

        start_time = time.perf_counter()

        # =====================================================
        # VALIDATE CONVERSATION OWNERSHIP
        # =====================================================

        conversation_id = (
            self.memory.get_or_create_conversation(
                conversation_id
            )
        )

        # =====================================================
        # SAVE USER MESSAGE
        # =====================================================

        self.memory.save_message(
            conversation_id=conversation_id,
            role="user",
            content=message,
        )

        # =====================================================
        # LOAD CONVERSATION HISTORY
        # =====================================================

        history = self.memory.get_messages(
            conversation_id
        )

        langchain_messages = []

        for item in history:

            if item["role"] == "user":

                langchain_messages.append(
                    HumanMessage(
                        content=item["content"]
                    )
                )

            elif item["role"] == "assistant":

                langchain_messages.append(
                    AIMessage(
                        content=item["content"]
                    )
                )

        # =====================================================
        # AGENT STARTED
        # =====================================================

        record_audit_event(
            self.db,
            correlation_id=self.correlation_id,
            conversation_id=conversation_id,
            employee_id=self.employee_id,
            event_type="AGENT_STARTED",
            status="STARTED",
        )

        try:

            # =================================================
            # CREATE LANGGRAPH
            # =================================================

            graph = create_hr_graph(
                db=self.db,
                employee_id=self.employee_id,
                correlation_id=self.correlation_id,
                conversation_id=conversation_id,
            )

            # =================================================
            # EXECUTE LANGGRAPH
            # =================================================

            result = graph.invoke(
                {
                    "messages": langchain_messages,
                    "employee_id": self.employee_id,
                }
            )

            # =================================================
            # GET FINAL ASSISTANT MESSAGE
            # =================================================

            final_message = result["messages"][-1]

            response = final_message.content

            # =================================================
            # AGENT COMPLETED
            # =================================================

            duration_ms = (
                time.perf_counter()
                - start_time
            ) * 1000

            record_audit_event(
                self.db,
                correlation_id=self.correlation_id,
                conversation_id=conversation_id,
                employee_id=self.employee_id,
                event_type="AGENT_COMPLETED",
                status="SUCCESS",
                duration_ms=duration_ms,
            )

            # =================================================
            # SAVE ASSISTANT MESSAGE
            # =================================================

            self.memory.save_message(
                conversation_id=conversation_id,
                role="assistant",
                content=response,
            )

            return response

        except Exception as exc:

            # =================================================
            # AGENT FAILED
            # =================================================

            duration_ms = (
                time.perf_counter()
                - start_time
            ) * 1000

            record_audit_event(
                self.db,
                correlation_id=self.correlation_id,
                conversation_id=conversation_id,
                employee_id=self.employee_id,
                event_type="AGENT_FAILED",
                status="FAILED",
                duration_ms=duration_ms,
                error_type=type(exc).__name__,
            )

            # Do not expose the exception here.
            # chat_routes.py handles the HTTP response.
            raise