import base64
import time
from typing import Dict, Optional, Tuple
from sarvamai import SarvamAI


# Curated voice presets for podcast hosts
AVAILABLE_VOICES = {
    "rohan": {"gender": "male", "description": "Dynamic, clear, conversational"},
    "priya": {"gender": "female", "description": "Insightful, warm, articulate"},
    "rahul": {"gender": "male", "description": "Friendly, approachable"},
    "simran": {"gender": "female", "description": "Lively, energetic, engaging"},
    "ashutosh": {"gender": "male", "description": "Authoritative, deep, thoughtful"},
    "kavya": {"gender": "female", "description": "Expressive, storytelling"},
    "shubh": {"gender": "male", "description": "Narrative, radio-host style"},
    "roopa": {"gender": "female", "description": "Warm, conversational"},
    "aditya": {"gender": "male", "description": "Professional, crisp"},
    "ritu": {"gender": "female", "description": "Bright, clear"},
}


class VoiceSynthesizer:
    """
    Synthesizes speech for podcast dialogue lines using Sarvam AI's Bulbul v3 TTS.
    """

    def __init__(
        self,
        client: Optional[SarvamAI] = None,
        language_code: str = "en-IN",
        speaker_mapping: Optional[Dict[str, str]] = None,
        pace: float = 1.0,
        pitch: float = 0.0,
    ):
        self.client = client or SarvamAI()
        self.language_code = language_code
        self.pace = pace
        self.pitch = pitch

        # Default speaker mapping: Rohan -> rohan, Priya -> priya
        self.speaker_mapping = speaker_mapping or {
            "rohan": "rohan",
            "priya": "priya",
        }

    def get_voice_for_speaker(self, speaker_name: str) -> str:
        """Finds or assigns the appropriate Sarvam voice for a speaker."""
        lookup_key = speaker_name.lower().strip()
        if lookup_key in self.speaker_mapping:
            return self.speaker_mapping[lookup_key]

        # Check direct match with available voices
        for voice in AVAILABLE_VOICES:
            if voice in lookup_key:
                return voice

        # Fallback alternating assignment
        return "rohan"

    def synthesize_line(
        self,
        text: str,
        speaker_name: str,
        pace: Optional[float] = None,
        pitch: Optional[float] = None,
        max_retries: int = 3,
    ) -> bytes:
        """
        Converts a line of text to WAV audio bytes.
        """
        voice = self.get_voice_for_speaker(speaker_name)
        text = text.strip()
        if not text:
            return b""

        effective_pace = pace if pace is not None else self.pace
        effective_pitch = pitch if pitch is not None else self.pitch

        for attempt in range(max_retries):
            try:
                response = self.client.text_to_speech.convert(
                    text=text,
                    language_code=self.language_code,
                    speaker=voice,
                    model="bulbul:v3",
                    output_audio_codec="wav",
                    pace=effective_pace,
                    pitch=effective_pitch,
                    enable_preprocessing=True,
                )

                if response.audios and len(response.audios) > 0:
                    raw_b64 = response.audios[0]
                    return base64.b64decode(raw_b64)
                raise RuntimeError("Sarvam TTS returned an empty audio list.")

            except Exception as e:
                if attempt == max_retries - 1:
                    raise RuntimeError(f"Failed to synthesize audio for [{speaker_name} ({voice})]: {e}")
                time.sleep(1.0 * (attempt + 1))

        return b""
