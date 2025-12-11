

import os
import requests
import json
from dotenv import load_dotenv
from elevenlabs import ElevenLabs

# Load environment variables
load_dotenv()

eleven_key = os.getenv("ELEVENLABS_API_KEY")
voice_id = os.getenv("VOICE_ID")

# ElevenLabs TTS client
tts = ElevenLabs(api_key=eleven_key)


def generate_script(topic):
    prompt = f"""
    Create a natural, engaging podcast script about: {topic}.
    Length: 2 to 3 minutes.
    Tone: conversational, friendly, and human.
    Write the script as if talking directly to listeners.
    """

    payload = {
        "model": "llama3.2:3b",
        "prompt": prompt
    }

    print("Generating script with Ollama...")

    response = requests.post(
        "http://localhost:11434/api/generate",
        json=payload,
        stream=True
    )

    script = ""

    for line in response.iter_lines():
        if line:
            data = json.loads(line)
            if "response" in data:
                script += data["response"]

    return script


def generate_audio(script, filename="podcast.mp3"):
    print("Generating audio with ElevenLabs...")

    audio = tts.text_to_speech.convert(
        voice_id=voice_id,
        text=script,
        model_id="eleven_multilingual_v2"
    )

    with open(filename, "wb") as f:
        for chunk in audio:
            f.write(chunk)

    print(f"Podcast saved as: {filename}")


def main():
    topic = input("Enter your podcast topic: ")

    print("\nGenerating script...")
    script = generate_script(topic)

    print("\n=== RAW SCRIPT OUTPUT ===\n")
    print(repr(script))   # shows empty strings or whitespace


    print("\nConverting to audio...")
    generate_audio(script)



if __name__ == "__main__":
    main()
