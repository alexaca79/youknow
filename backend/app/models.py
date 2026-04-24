from pydantic import BaseModel, Field


class PromptRequest(BaseModel):
    recent_prompts: list[str] = Field(default_factory=list, max_length=20)


class PromptResponse(BaseModel):
    technicalThing: str
    everydayThing: str
    fullPrompt: str
    rationaleHint: str


class SpeechRequest(BaseModel):
    text: str = Field(min_length=1, max_length=400)
    voice: str | None = Field(default=None, max_length=80)
