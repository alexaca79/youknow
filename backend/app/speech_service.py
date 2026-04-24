from __future__ import annotations

from html import escape
from urllib.parse import urlparse

import azure.cognitiveservices.speech as speechsdk
from azure.core.exceptions import ClientAuthenticationError
from azure.identity import DefaultAzureCredential

from .config import Settings


class SpeechService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._credential = DefaultAzureCredential()
        self._base_endpoint = self._build_base_endpoint(settings.speech_endpoint)

    @property
    def is_configured(self) -> bool:
        return bool(self._base_endpoint and self._settings.speech_resource_id)

    def synthesize_prompt_audio(self, text: str, voice: str | None = None) -> bytes:
        if not self.is_configured:
            raise RuntimeError("Azure Speech is not configured.")

        cleaned_text = text.strip()
        if not cleaned_text:
            raise RuntimeError("Speech text cannot be empty.")

        speech_config = self._create_speech_config()
        speech_config.set_speech_synthesis_output_format(
            speechsdk.SpeechSynthesisOutputFormat.Riff8Khz8BitMonoMULaw
        )
        synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=None)

        ssml = self._build_excited_ssml(cleaned_text, voice or self._settings.speech_voice)
        result = synthesizer.speak_ssml_async(ssml).get()
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted and result.audio_data:
            return bytes(result.audio_data)

        if result.reason == speechsdk.ResultReason.Canceled:
            cancellation = result.cancellation_details
            detail = f"Speech synthesis canceled: {cancellation.reason}"
            if cancellation.reason == speechsdk.CancellationReason.Error and cancellation.error_details:
                detail = cancellation.error_details
            raise RuntimeError(detail)

        raise RuntimeError(f"Speech synthesis finished with unexpected result: {result.reason}")

    def _create_speech_config(self) -> speechsdk.SpeechConfig:
        try:
            token = self._credential.get_token("https://cognitiveservices.azure.com/.default")
        except ClientAuthenticationError as exc:
            raise RuntimeError(
                "Azure authentication failed for Azure Speech. Run 'az login' or configure DefaultAzureCredential."
            ) from exc

        speech_config = speechsdk.SpeechConfig(endpoint=self._base_endpoint)
        speech_config.authorization_token = (
            f"aad#{self._settings.speech_resource_id}#{token.token}"
        )
        return speech_config

    @staticmethod
    def _build_base_endpoint(endpoint_url: str | None) -> str | None:
        if not endpoint_url:
            return None

        parsed = urlparse(endpoint_url)
        if not parsed.scheme or not parsed.netloc:
            raise RuntimeError(
                "AZURE_SPEECH_ENDPOINT must be a full HTTPS endpoint, for example https://your-resource.cognitiveservices.azure.com/."
            )
        return f"{parsed.scheme}://{parsed.netloc}"

    @staticmethod
    def _build_excited_ssml(text: str, voice: str) -> str:
        safe_text = escape(text)
        safe_voice = escape(voice)
        return f"""<speak version='1.0' xml:lang='en-US' xmlns='http://www.w3.org/2001/10/synthesis' xmlns:mstts='http://www.w3.org/2001/mstts'>
  <voice name='{safe_voice}'>
    <mstts:express-as style='excitement'>
      {safe_text}
    </mstts:express-as>
  </voice>
</speak>"""