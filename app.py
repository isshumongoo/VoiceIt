from pathlib import Path

import podcast_generator as pg


def run_generation(topic: str, style: str, duration_minutes: int, model: str, skip_audio: bool, output_dir: Path):
    """Compatibility wrapper that supports both new and older podcast_generator modules."""
    if hasattr(pg, "generate_podcast"):
        return pg.generate_podcast(
            topic=topic,
            style=style,
            duration_minutes=duration_minutes,
            model=model,
            output_dir=output_dir,
            skip_audio=skip_audio,
        )

    if not hasattr(pg, "generate_script"):
        raise RuntimeError("podcast_generator.py is missing generate_script/generate_podcast.")

    script_path, audio_path = pg.make_output_paths(topic, output_dir)
    script = pg.generate_script(topic=topic, style=style, duration_minutes=duration_minutes, model=model)
    pg.save_script(script, script_path)

    result = {"script": script, "script_path": str(script_path), "audio_path": ""}
    if skip_audio:
        return result

    eleven_key = pg.os.getenv("ELEVENLABS_API_KEY")
    voice_id = pg.os.getenv("VOICE_ID")
    if not eleven_key or not voice_id:
        raise RuntimeError("Missing ELEVENLABS_API_KEY or VOICE_ID in environment.")

    pg.generate_audio(script, audio_path, voice_id=voice_id, api_key=eleven_key)
    result["audio_path"] = str(audio_path)
    return result


def create_app():
    from dotenv import load_dotenv
    from flask import Flask, jsonify, render_template, request, send_file

    load_dotenv()
    app = Flask(__name__)
    app.config["OUTPUT_DIR"] = getattr(pg, "DEFAULT_OUTPUT_DIR", Path("output"))

    @app.get("/")
    def index():
        return render_template("index.html", default_model=getattr(pg, "DEFAULT_MODEL", "llama3.2:3b"))

    @app.post("/api/generate")
    def api_generate():
        payload = request.get_json(silent=True) or {}
        topic = (payload.get("topic") or "").strip()
        style = (payload.get("style") or "conversational").strip()
        duration = int(payload.get("duration_minutes") or 3)
        model = (payload.get("model") or getattr(pg, "DEFAULT_MODEL", "llama3.2:3b")).strip()
        skip_audio = bool(payload.get("skip_audio", False))

        if not topic:
            return jsonify({"error": "Topic is required."}), 400

        try:
            result = run_generation(
                topic=topic,
                style=style,
                duration_minutes=duration,
                model=model,
                skip_audio=skip_audio,
                output_dir=Path(app.config["OUTPUT_DIR"]),
            )
            return jsonify(result)
        except Exception as exc:
            return jsonify({"error": str(exc)}), 500

    def _safe_output_file(raw_path: str):
        if not raw_path:
            return None
        output_dir = Path(app.config["OUTPUT_DIR"]).resolve()
        file_path = Path(raw_path).resolve()
        if output_dir not in file_path.parents:
            return None
        if not file_path.exists():
            return None
        return file_path

    @app.get("/download/script")
    def download_script():
        path = _safe_output_file(request.args.get("path", ""))
        if not path:
            return jsonify({"error": "Script file not found."}), 404
        return send_file(path, as_attachment=True)

    @app.get("/download/audio")
    def download_audio():
        path = _safe_output_file(request.args.get("path", ""))
        if not path:
            return jsonify({"error": "Audio file not found."}), 404
        return send_file(path, as_attachment=True)

    return app


if __name__ == "__main__":
    create_app().run(host="0.0.0.0", port=5000, debug=True)
