from pydantic import BaseModel, ConfigDict, Field


class ChatRequest(BaseModel):
    """Request body for POST /chat."""

    message: str = Field(min_length=1, max_length=2000, description="The user's chat message.")

    model_config = ConfigDict(str_strip_whitespace=True)


class ChatResponse(BaseModel):
    """Response body for POST /chat."""

    text: str = Field(description="The LLM's reply.")
