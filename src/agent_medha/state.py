import operator
from typing import Annotated, List, TypedDict, Union, Optional

from langchain_core.messages import BaseMessage
from langchain_core.documents import Document


class AgentState(TypedDict):
    """
    The state of the agent.
    
    Attributes:
        messages: Conversation history
        next_step: Next step/node to execute
        context: Retrieved context from memory
        session_id: Unique identifier for this conversation session
        working_memory: Short-term working memory for current session
    """
    messages: Annotated[List[BaseMessage], operator.add]
    next_step: str
    context: List[Document]
    session_id: Optional[str]
    working_memory: Optional[dict]
