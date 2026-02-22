# VoiceIt

VoiceIt is a command-line podcast generator that:
1. Drafts a spoken podcast script using a local Ollama model.
2. Converts that script to MP3 audio using ElevenLabs text-to-speech.

## Features

- Interactive prompt or one-line CLI usage
- Configurable tone/style and duration target
- Script + audio output with timestamped filenames
- Optional script-only mode (`--skip-audio`)

## Requirements

- Python 3.10+
- [Ollama](https://ollama.com/) running locally on `http://localhost:11434`
- ElevenLabs API key + voice ID

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

## Usage

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

### Custom output paths

```bash
python podcast_generator.py "Startup lessons" --script-file output/custom_script.txt --audio-file output/custom_audio.mp3
```

Generated files default to the `output/` directory.
