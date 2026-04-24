from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from urllib.parse import urlparse

import azure.cognitiveservices.speech as speechsdk
from azure.core.exceptions import ClientAuthenticationError
from azure.identity import DefaultAzureCredential


DEFAULT_TEXT = "Hello, welcome to Azure AI Foundry!"
DEFAULT_VOICE = "en-US-Grant:MAI-Voice-1"


def _get_required_env(name: str) -> str:
    value = os.getenv(name)
    if value:
        return value
    raise RuntimeError(f"Missing required environment variable: {name}")


def _build_base_endpoint(endpoint_url: str) -> str:
    parsed = urlparse(endpoint_url)
    if not parsed.scheme or not parsed.netloc:
        raise RuntimeError(
            "AZURE_SPEECH_ENDPOINT must be a full HTTPS endpoint, for example "
            "https://your-resource.cognitiveservices.azure.com/"
        )
    return f"{parsed.scheme}://{parsed.netloc}"


def _create_speech_config(base_endpoint: str, resource_id: str) -> speechsdk.SpeechConfig:
    credential = DefaultAzureCredential()
    token = credential.get_token("https://cognitiveservices.azure.com/.default")

    speech_config = speechsdk.SpeechConfig(endpoint=base_endpoint)
    speech_config.authorization_token = f"aad#{resource_id}#{token.token}"
    return speech_config


def _create_audio_config(output_file: Path | None) -> speechsdk.audio.AudioOutputConfig:
    if output_file is None:
        return speechsdk.audio.AudioOutputConfig(use_default_speaker=True)

    output_file.parent.mkdir(parents=True, exist_ok=True)
    return speechsdk.audio.AudioOutputConfig(filename=str(output_file))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Synthesize text to speech with Azure AI Speech using DefaultAzureCredential."
    )
    parser.add_argument(
        "--text",
        default=os.getenv("AZURE_SPEECH_TEXT", DEFAULT_TEXT),
        help="Text to synthesize. Defaults to AZURE_SPEECH_TEXT or a sample sentence.",
    )
    parser.add_argument(
        "--voice",
        default=os.getenv("AZURE_SPEECH_VOICE", DEFAULT_VOICE),
        help="Speech voice name. Defaults to AZURE_SPEECH_VOICE or en-US-Grant:MAI-Voice-1.",
    )
    parser.add_argument(
        "--output-file",
        default=os.getenv("AZURE_SPEECH_OUTPUT_FILE"),
        help="Optional file path to save the synthesized audio. If omitted, audio plays on the default speaker.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    try:
        endpoint = _get_required_env("AZURE_SPEECH_ENDPOINT")
        resource_id = _get_required_env("AZURE_RESOURCE_ID")
        base_endpoint = _build_base_endpoint(endpoint)
        speech_config = _create_speech_config(base_endpoint, resource_id)
    except ClientAuthenticationError as exc:
        print(
            "Azure authentication failed. Run 'az login' or configure a supported DefaultAzureCredential source.",
            file=sys.stderr,
        )
        print(str(exc), file=sys.stderr)
        return 1
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    speech_config.speech_synthesis_voice_name = args.voice

    output_path = Path(args.output_file).expanduser().resolve() if args.output_file else None
    audio_config = _create_audio_config(output_path)
    synthesizer = speechsdk.SpeechSynthesizer(
        speech_config=speech_config,
        audio_config=audio_config,
    )

    result = synthesizer.speak_text_async(args.text).get()
    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        if output_path is None:
            print(f"Speech synthesized and played for text: {args.text}")
        else:
            print(f"Speech synthesized to file: {output_path}")
        return 0

    if result.reason == speechsdk.ResultReason.Canceled:
        cancellation = result.cancellation_details
        print(f"Speech synthesis canceled: {cancellation.reason}", file=sys.stderr)
        if cancellation.reason == speechsdk.CancellationReason.Error and cancellation.error_details:
            print(cancellation.error_details, file=sys.stderr)
        return 1

    print(f"Speech synthesis finished with unexpected result: {result.reason}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())