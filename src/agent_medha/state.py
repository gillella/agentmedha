import operator
from typing import Annotated, List, TypedDict, Union

from langchain_core.messages import BaseMessage
from langchain_core.documents import Document

class AgentState(TypedDict):
    """The state of the agent."""
    messages: Annotated[List[BaseMessage], operator.add]
    next_step: str
    context: List[Document]
