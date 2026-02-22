from pathlib import Path

from podcast_generator import build_parser, build_prompt, make_output_paths, slugify


def test_slugify_replaces_special_characters():
    assert slugify("AI & The Future!!!") == "ai-the-future"


def test_build_prompt_contains_requested_constraints():
    prompt = build_prompt("Space Travel", "playful", 5)
    assert "Space Travel" in prompt
    assert "playful" in prompt
    assert "5 minutes" in prompt


def test_make_output_paths_returns_timestamped_paths():
    script_path, audio_path = make_output_paths("Demo topic", Path("output"))
    assert script_path.parent == Path("output")
    assert script_path.suffix == ".txt"
    assert audio_path.suffix == ".mp3"


def test_parser_supports_web_related_cli_options():
    args = build_parser().parse_args(["Topic", "--skip-audio", "--style", "deep"])
    assert args.topic == "Topic"
    assert args.skip_audio is True
    assert args.style == "deep"
