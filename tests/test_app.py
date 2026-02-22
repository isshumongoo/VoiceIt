from pathlib import Path

import app


def test_run_generation_uses_generate_podcast_when_available(monkeypatch):
    called = {}

    def fake_generate_podcast(**kwargs):
        called.update(kwargs)
        return {"script": "hello", "script_path": "a.txt", "audio_path": ""}

    monkeypatch.setattr(app.pg, "generate_podcast", fake_generate_podcast, raising=False)
    result = app.run_generation("topic", "style", 3, "model", True, Path("output"))

    assert result["script"] == "hello"
    assert called["topic"] == "topic"


def test_run_generation_fallback_without_generate_podcast(monkeypatch, tmp_path):
    monkeypatch.delattr(app.pg, "generate_podcast", raising=False)

    monkeypatch.setattr(app.pg, "make_output_paths", lambda topic, out: (tmp_path / "s.txt", tmp_path / "a.mp3"))
    monkeypatch.setattr(app.pg, "generate_script", lambda **kwargs: "script")
    monkeypatch.setattr(app.pg, "save_script", lambda script, path: path.write_text(script, encoding="utf-8"))

    result = app.run_generation("topic", "style", 3, "model", True, tmp_path)

    assert result["script"] == "script"
    assert Path(result["script_path"]).exists()
    assert result["audio_path"] == ""
