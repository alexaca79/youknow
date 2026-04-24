from enum import Enum

from pydantic import BaseModel, Field


class Specialty(str, Enum):
    data_ai = "data-ai"
    apps_ai = "apps-ai"
    infra = "infra"


class Difficulty(str, Enum):
    normal = "normal"
    hard = "hard"
    non_sequitur = "non-sequitur"


class PromptRequest(BaseModel):
    recent_prompts: list[str] = Field(default_factory=list, max_length=20)
    specialty: Specialty = Field(default=Specialty.data_ai)
    difficulty: Difficulty = Field(default=Difficulty.normal)


class PromptResponse(BaseModel):
    technicalThing: str
    everydayThing: str
    fullPrompt: str
    rationaleHint: str


class SpeechRequest(BaseModel):
    text: str = Field(min_length=1, max_length=400)
    voice: str | None = Field(default=None, max_length=80)
