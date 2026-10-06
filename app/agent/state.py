from typing import Annotated, TypedDict

from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage


class HRAgentState(TypedDict):
    """
    State maintained throughout an HR conversation.
    """

    messages: Annotated[list[BaseMessage], add_messages]

    employee_id: str