import json
import re
from collections import deque
from pathlib import Path
from urllib.parse import urlparse

from openai import OpenAI

from .config import Settings
from .models import PromptResponse

_FENCE_RE = re.compile(r"```(?:json)?\s*([\s\S]*?)```", re.IGNORECASE)
_PROMPTS_DIR = Path(__file__).resolve().parent.parent.parent / "prompts"
_USER_PROMPT_TEMPLATE = (_PROMPTS_DIR / "user.md").read_text(encoding="utf-8")
_SYSTEM_PROMPTS: dict[str, str] = {
    "data-ai": (_PROMPTS_DIR / "system-data-ai.md").read_text(encoding="utf-8"),
    "apps-ai": (_PROMPTS_DIR / "system-apps-ai.md").read_text(encoding="utf-8"),
    "infra": (_PROMPTS_DIR / "system-infra.md").read_text(encoding="utf-8"),
}
_DIFFICULTY_INSTRUCTIONS: dict[str, str] = {
    "normal": (
        "\n## Difficulty: Normal\n"
        "- everydayThing should be a relatable, recognizable everyday situation that most people understand.\n"
        "- The analogy should be fun but the connection between technicalThing and everydayThing should be reasonably intuitive to explain.\n"
    ),
    "hard": (
        "\n## Difficulty: Hard\n"
        "- everydayThing should be an unusual, niche, or surprising everyday situation that makes the analogy much harder to explain.\n"
        "- The connection should still exist but require real creativity and lateral thinking to articulate.\n"
        "- The speaker will need to dig deep to find the shared pattern.\n"
    ),
    "non-sequitur": (
        "\n## Difficulty: Non Sequitur\n"
        "- everydayThing should be completely random, absurd, and seemingly unrelated to technicalThing.\n"
        "- There is no obvious connection — the speaker must invent one on the spot.\n"
        "- rationaleHint should still offer one possible angle, but it can be a stretch.\n"
        "- This is chaos mode — make it wild, weird, and hilarious.\n"
    ),
}


class PromptGenerator:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client = self._create_client(settings) if self._can_configure(settings) else None
        self._recent_prompts: deque[str] = deque(maxlen=200)

    @property
    def is_configured(self) -> bool:
        return self._client is not None

    def generate_prompt(self, recent_prompts: list[str], specialty: str = "data-ai", difficulty: str = "normal") -> PromptResponse:
        if self._client is None:
            raise RuntimeError(
                "Azure OpenAI is not configured. Set AZURE_OPENAI_API_KEY or "
                "configure OPENAI_BASE_URL with an Azure endpoint and run 'az login'."
            )

        avoid_prompts = [prompt.strip() for prompt in recent_prompts if prompt.strip()]
        avoid_prompts.extend(self._recent_prompts)
        normalized_avoid = {self._normalize(prompt) for prompt in avoid_prompts}

        last_error: Exception | None = None
        for _ in range(4):
            raw_payload = self._request_prompt(avoid_prompts, specialty, difficulty)
            try:
                prompt = PromptResponse(**json.loads(raw_payload))
            except Exception as exc:
                last_error = exc
                continue

            normalized_prompt = self._normalize(prompt.fullPrompt)
            if normalized_prompt in normalized_avoid:
                continue

            self._recent_prompts.append(prompt.fullPrompt)
            return prompt

        if last_error is not None:
            raise RuntimeError("The model returned a response that could not be parsed.") from last_error

        raise RuntimeError("Unable to generate a unique prompt after several attempts.")

    def _request_prompt(self, avoid_prompts: list[str], specialty: str, difficulty: str) -> str:
        avoid_text = "\n".join(f"- {prompt}" for prompt in avoid_prompts[-25:]) or "- none yet"
        user_prompt = _USER_PROMPT_TEMPLATE.replace("{avoid_list}", avoid_text)
        system_prompt = _SYSTEM_PROMPTS.get(specialty, _SYSTEM_PROMPTS["data-ai"])
        system_prompt += _DIFFICULTY_INSTRUCTIONS.get(difficulty, _DIFFICULTY_INSTRUCTIONS["normal"])
        response = self._client.chat.completions.create(
            model=self._settings.openai_model,
            temperature=1.2,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        content = response.choices[0].message.content
        if not content:
            raise RuntimeError("The model returned an empty response.")
        # Strip markdown code fences that some models wrap around JSON
        fence_match = _FENCE_RE.search(content)
        if fence_match:
            return fence_match.group(1).strip()
        return content.strip()

    @staticmethod
    def _normalize(value: str) -> str:
        return " ".join(value.lower().strip().split())

    @staticmethod
    def _can_configure(settings: Settings) -> bool:
        if settings.openai_api_key:
            return True
        base_url = settings.openai_base_url or ""
        return ".openai.azure.com" in base_url

    @staticmethod
    def _create_client(settings: Settings) -> OpenAI:
        base_url = PromptGenerator._normalize_base_url(settings.openai_base_url)
        if settings.openai_api_key:
            api_key: str | object = settings.openai_api_key
        elif base_url and ".openai.azure.com" in base_url:
            from azure.identity import DefaultAzureCredential, get_bearer_token_provider

            api_key = get_bearer_token_provider(
                DefaultAzureCredential(),
                "https://cognitiveservices.azure.com/.default",
            )
        else:
            raise RuntimeError("No API key or Azure endpoint configured for OpenAI.")

        client_kwargs: dict[str, object] = {"api_key": api_key}
        if base_url:
            client_kwargs["base_url"] = base_url
        return OpenAI(**client_kwargs)

    @staticmethod
    def _normalize_base_url(base_url: str | None) -> str | None:
        if not base_url:
            return None

        normalized = base_url.rstrip("/")
        parsed = urlparse(normalized)
        if not parsed.scheme or not parsed.netloc:
            return normalized

        if parsed.netloc.endswith(".openai.azure.com") and not parsed.path.endswith("/openai/v1"):
            return f"{parsed.scheme}://{parsed.netloc}/openai/v1"

        return normalized
