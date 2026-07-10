"""Speech-to-text (Groq Whisper) and text-to-speech (Deepgram)."""
import os
from groq import Groq
from deepgram import DeepgramClient

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
deepgram_client = DeepgramClient(api_key=os.getenv("DEEPGRAM_API_KEY"))

""" transcribe_audio: convert audio bytes to text using Groq Whisper."""

def transcribe_audio(audio_bytes: bytes, filename: str = "voice.ogg", language: str = "en") -> str:
    transcription = groq_client.audio.transcriptions.create(
        file=(filename, audio_bytes),
        model="whisper-large-v3-turbo",
        response_format="text",
        language=language,
    )
    return transcription

""" synthesize_speech: convert text to speech using Deepgram Aura-2."""

def synthesize_speech(text: str, voice: str = "aura-2-thalia-en") -> bytes:
    """Convert text to speech using Deepgram Aura-2. Returns MP3 bytes, ready to send."""
    response = deepgram_client.speak.v1.audio.generate(
        text=text,
        model=voice,
    )

    # Handle both possible SDK response shapes
    if hasattr(response, "stream"):
        return response.stream.getvalue()
    else:
        # response is a generator/iterator yielding bytes chunks
        return b"".join(chunk for chunk in response)