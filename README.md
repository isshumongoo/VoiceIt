# VoiceIt

VoiceIt is now both:
- a **CLI podcast generator**, and
- a **web UI** for generating scripts/audio from your browser.

It uses Ollama to draft a script and ElevenLabs to produce MP3 narration.

## Features

- Browser UI (`/`) with form-based generation
- JSON API endpoint (`POST /api/generate`)
- Download links for generated script/audio artifacts
- CLI mode with configurable style, duration, and model
- Optional script-only mode (`--skip-audio`)

## Requirements

- Python 3.10+
- [Ollama](https://ollama.com/) running locally on `http://localhost:11434`
- ElevenLabs API key + voice ID (unless skipping audio)

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file:

```env
ELEVENLABS_API_KEY=your_api_key
VOICE_ID=your_voice_id
```

## Run the web app

```bash
python app.py
```

Then open: `http://localhost:5000`

## API usage

```bash
curl -X POST http://localhost:5000/api/generate \
  -H 'Content-Type: application/json' \
  -d '{"topic":"AI for creators","style":"energetic","duration_minutes":3,"model":"llama3.2:3b"}'
```

## CLI usage

### Interactive

```bash
python podcast_generator.py
```

### Direct topic input

```bash
python podcast_generator.py "The rise of local AI models"
```

### Script-only mode

```bash
python podcast_generator.py "Productivity habits" --style "motivational" --duration-minutes 4 --skip-audio
```

Generated files default to the `output/` directory.
