import argparse
import json
import os
import textwrap
from datetime import datetime
from pathlib import Path


OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "llama3.2:3b"
DEFAULT_OUTPUT_DIR = Path("output")
DEFAULT_VOICE_MODEL = "eleven_multilingual_v2"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate podcast scripts with Ollama and convert them to speech with ElevenLabs."
    )
    parser.add_argument("topic", nargs="?", help="Podcast topic. If omitted, prompt interactively.")
    parser.add_argument("--style", default="conversational", help="Style or vibe for the podcast script.")
    parser.add_argument("--duration-minutes", type=int, default=3, help="Approximate target duration in minutes.")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Ollama model name.")
    parser.add_argument(
        "--script-file",
        type=Path,
        help="Optional path to save the generated script as text.",
    )
    parser.add_argument(
        "--audio-file",
        type=Path,
        help="Optional explicit path for generated audio file.",
    )
    parser.add_argument(
        "--skip-audio",
        action="store_true",
        help="Generate only the script and skip ElevenLabs audio output.",
    )
    return parser


def slugify(value: str) -> str:
    cleaned = "".join(char.lower() if char.isalnum() else "-" for char in value).strip("-")
    while "--" in cleaned:
        cleaned = cleaned.replace("--", "-")
    return cleaned[:60] or "podcast"


def build_prompt(topic: str, style: str, duration_minutes: int) -> str:
    return textwrap.dedent(
        f"""
        Create a natural, engaging podcast script about: {topic}

        Requirements:
        - Length: approximately {duration_minutes} minutes.
        - Tone: {style}, warm, and human.
        - Open with a hook in the first 2-3 lines.
        - Include clear transitions between sections.
        - End with a concise recap and one call-to-action.
        - Write as spoken dialogue suitable for text-to-speech.
        """
    ).strip()


def generate_script(topic: str, style: str, duration_minutes: int, model: str) -> str:
    payload = {
        "model": model,
        "prompt": build_prompt(topic, style, duration_minutes),
    }

    print("Generating script with Ollama...")
    import requests

    response = requests.post(OLLAMA_URL, json=payload, stream=True, timeout=180)
    response.raise_for_status()

    script_parts = []
    for line in response.iter_lines():
        if not line:
            continue
        data = json.loads(line)
        if "response" in data:
            script_parts.append(data["response"])

    script = "".join(script_parts).strip()
    if not script:
        raise RuntimeError("Ollama returned an empty script.")
    return script


def make_output_paths(topic: str, output_dir: Path) -> tuple[Path, Path]:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    stem = f"{timestamp}_{slugify(topic)}"
    return output_dir / f"{stem}.txt", output_dir / f"{stem}.mp3"


def save_script(script: str, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(script, encoding="utf-8")
    print(f"Script saved to: {path}")


def generate_audio(script: str, filename: Path, voice_id: str, api_key: str) -> None:
    print("Generating audio with ElevenLabs...")

    from elevenlabs import ElevenLabs

    tts = ElevenLabs(api_key=api_key)
    audio = tts.text_to_speech.convert(
        voice_id=voice_id,
        text=script,
        model_id=DEFAULT_VOICE_MODEL,
    )

    filename.parent.mkdir(parents=True, exist_ok=True)
    with open(filename, "wb") as file_obj:
        for chunk in audio:
            file_obj.write(chunk)

    print(f"Podcast saved as: {filename}")


def resolve_topic(cli_topic: str | None) -> str:
    if cli_topic:
        return cli_topic.strip()
    return input("Enter your podcast topic: ").strip()


def main() -> None:
    from dotenv import load_dotenv

    load_dotenv()
    parser = build_parser()
    args = parser.parse_args()

    topic = resolve_topic(args.topic)
    if not topic:
        raise SystemExit("Topic cannot be empty.")

    script_path_default, audio_path_default = make_output_paths(topic, DEFAULT_OUTPUT_DIR)
    script_file = args.script_file or script_path_default
    audio_file = args.audio_file or audio_path_default

    script = generate_script(
        topic=topic,
        style=args.style,
        duration_minutes=args.duration_minutes,
        model=args.model,
    )

    save_script(script, script_file)

    if args.skip_audio:
        print("Audio generation skipped (--skip-audio).")
        return

    eleven_key = os.getenv("ELEVENLABS_API_KEY")
    voice_id = os.getenv("VOICE_ID")

    if not eleven_key or not voice_id:
        raise SystemExit("Missing ELEVENLABS_API_KEY or VOICE_ID in environment.")

    generate_audio(script, audio_file, voice_id=voice_id, api_key=eleven_key)


if __name__ == "__main__":
    main()
