from pathlib import Path

from podcast_generator import DEFAULT_MODEL, DEFAULT_OUTPUT_DIR, generate_podcast


def create_app():
    from dotenv import load_dotenv
    from flask import Flask, jsonify, render_template, request, send_file

    load_dotenv()
    app = Flask(__name__)
    app.config["OUTPUT_DIR"] = DEFAULT_OUTPUT_DIR

    @app.get("/")
    def index():
        return render_template("index.html", default_model=DEFAULT_MODEL)

    @app.post("/api/generate")
    def api_generate():
        payload = request.get_json(silent=True) or {}
        topic = (payload.get("topic") or "").strip()
        style = (payload.get("style") or "conversational").strip()
        duration = int(payload.get("duration_minutes") or 3)
        model = (payload.get("model") or DEFAULT_MODEL).strip()
        skip_audio = bool(payload.get("skip_audio", False))

        if not topic:
            return jsonify({"error": "Topic is required."}), 400

        try:
            result = generate_podcast(
                topic=topic,
                style=style,
                duration_minutes=duration,
                model=model,
                output_dir=Path(app.config["OUTPUT_DIR"]),
                skip_audio=skip_audio,
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
