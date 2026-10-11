import math
import wave
import numpy as np
from typing import Optional


class BGMGenerator:
    """
    Generates procedural background music and blends it with podcast dialogue
    using smooth acoustic ducking and intro/outro jingles.
    """

    CHORD_PROGRESSIONS = {
        "lofi_ambient": [
            # Cmaj9, Am9, Dm9, G13 (in Hz)
            ([261.63, 329.63, 392.00, 493.88, 587.33], 3.0),
            ([220.00, 261.63, 329.63, 392.00, 493.88], 3.0),
            ([146.83, 220.00, 261.63, 349.23, 440.00], 3.0),
            ([196.00, 246.94, 329.63, 392.00, 523.25], 3.0),
        ],
        "tech_upbeat": [
            # Fmaj7, G6, Em7, Am7
            ([174.61, 261.63, 329.63, 440.00], 2.5),
            ([196.00, 293.66, 392.00, 440.00], 2.5),
            ([164.81, 246.94, 329.63, 392.00], 2.5),
            ([220.00, 261.63, 329.63, 440.00], 2.5),
        ],
        "news_calm": [
            # Dm, Bb, F, C
            ([146.83, 220.00, 293.66, 349.23], 3.5),
            ([116.54, 174.61, 233.08, 293.66], 3.5),
            ([174.61, 220.00, 261.63, 349.23], 3.5),
            ([130.81, 196.00, 261.63, 329.63], 3.5),
        ],
    }

    def __init__(self, style: str = "lofi_ambient"):
        self.style = style if style in self.CHORD_PROGRESSIONS else "lofi_ambient"

    def generate_music_track(self, total_seconds: float, framerate: int = 22050) -> np.ndarray:
        """
        Synthesizes an ambient harmonic music track of arbitrary duration
        with soft bell/rhodes harmonics, gentle envelope decay, and smooth looping.
        """
        progression = self.CHORD_PROGRESSIONS[self.style]
        loop_duration = sum(dur for _, dur in progression)
        num_samples = int(total_seconds * framerate)
        music_signal = np.zeros(num_samples, dtype=np.float32)

        current_sample = 0
        chord_idx = 0

        while current_sample < num_samples:
            freqs, chord_dur = progression[chord_idx % len(progression)]
            chord_samples = int(chord_dur * framerate)
            t = np.linspace(0, chord_dur, chord_samples, endpoint=False)

            # Generate warm tone with fundamental and gentle harmonics
            chord_signal = np.zeros(chord_samples, dtype=np.float32)
            for f in freqs:
                # fundamental
                chord_signal += 0.12 * np.sin(2 * np.pi * f * t)
                # 2nd harmonic (warmth)
                chord_signal += 0.05 * np.sin(2 * np.pi * (2 * f) * t)
                # 3rd harmonic (sparkle)
                chord_signal += 0.02 * np.sin(2 * np.pi * (3 * f) * t)

            # Smooth envelope: fast attack, gentle exponential decay
            attack_len = int(0.08 * framerate)
            attack_env = np.linspace(0, 1, attack_len)
            decay_env = np.exp(-t[attack_len:] * 0.7)
            env = np.concatenate([attack_env, decay_env[: chord_samples - attack_len]])

            segment = chord_signal * env
            end_sample = min(current_sample + chord_samples, num_samples)
            actual_len = end_sample - current_sample
            music_signal[current_sample:end_sample] += segment[:actual_len]

            current_sample += chord_samples
            chord_idx += 1

        # Normalize music signal to avoid clipping
        max_val = np.max(np.abs(music_signal))
        if max_val > 0:
            music_signal = music_signal / max_val

        return music_signal

    def mix_dialogue_with_bgm(
        self,
        dialogue_pcm: bytes,
        framerate: int = 22050,
        intro_solo_sec: float = 2.5,
        outro_solo_sec: float = 3.0,
        bgm_full_volume: float = 0.22,
        bgm_duck_volume: float = 0.045,
    ) -> bytes:
        """
        Mixes speech dialogue with background music applying dynamic audio ducking.
        - Intro: Solo music plays for `intro_solo_sec`, smoothly ducking down before speech starts.
        - Speech: Music ducks down to `bgm_duck_volume` so speech is 100% clear.
        - Outro: Music swells back up to `bgm_full_volume` after speech ends, then fades to silence.
        """
        # Convert raw 16-bit PCM speech to float32 (-1.0 to 1.0)
        speech_int16 = np.frombuffer(dialogue_pcm, dtype=np.int16)
        speech_float = speech_int16.astype(np.float32) / 32768.0

        intro_samples = int(intro_solo_sec * framerate)
        outro_samples = int(outro_solo_sec * framerate)
        speech_samples = len(speech_float)

        total_samples = intro_samples + speech_samples + outro_samples
        total_seconds = total_samples / float(framerate)

        # Generate background music track matching full length
        bgm_signal = self.generate_music_track(total_seconds, framerate)

        # Build dynamic volume ducking envelope
        ducking_env = np.full(total_samples, bgm_duck_volume, dtype=np.float32)

        # Intro: Full volume fading down to ducked volume
        intro_fade_samples = int(1.0 * framerate)
        ducking_env[:intro_samples - intro_fade_samples] = bgm_full_volume
        ducking_env[intro_samples - intro_fade_samples : intro_samples] = np.linspace(
            bgm_full_volume, bgm_duck_volume, intro_fade_samples
        )

        # Outro: Ducked volume swelling up to full, then fading to 0
        speech_end = intro_samples + speech_samples
        outro_swell_samples = int(1.2 * framerate)
        ducking_env[speech_end : speech_end + outro_swell_samples] = np.linspace(
            bgm_duck_volume, bgm_full_volume, outro_swell_samples
        )
        ducking_env[speech_end + outro_swell_samples : -int(0.8 * framerate)] = bgm_full_volume
        ducking_env[-int(0.8 * framerate) :] = np.linspace(bgm_full_volume, 0.0, int(0.8 * framerate))

        # Smooth envelope to eliminate any clicks
        kernel_size = int(0.05 * framerate)
        kernel = np.ones(kernel_size) / kernel_size
        ducking_env = np.convolve(ducking_env, kernel, mode="same")

        # Blend ducked BGM with speech
        ducked_bgm = bgm_signal * ducking_env

        final_mix = np.copy(ducked_bgm)
        final_mix[intro_samples : intro_samples + speech_samples] += speech_float

        # Soft clipping / limiter to ensure no distortion
        final_mix = np.clip(final_mix, -0.98, 0.98)

        # Convert back to 16-bit PCM
        final_pcm = (final_mix * 32767.0).astype(np.int16).tobytes()
        return final_pcm
