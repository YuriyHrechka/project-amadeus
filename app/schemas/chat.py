from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ChatRequest(BaseModel):
    """Request body for POST /chat."""

    message: str = Field(min_length=1, max_length=2000, description="The user's chat message.")
    conversation_id: UUID | None = Field(
        default=None, description="Existing conversation to continue. Omit to start a new conversation."
    )
    user_id: UUID = Field(description="ID of the user sending the message.")

    model_config = ConfigDict(str_strip_whitespace=True)


class ChatResponse(BaseModel):
    """Response body for POST /chat."""

    text: str = Field(description="The LLM's reply.")
    conversation_id: UUID = Field(
        description="The conversation this exchange belongs to. Pass it back on the next request to continue it."
    )
