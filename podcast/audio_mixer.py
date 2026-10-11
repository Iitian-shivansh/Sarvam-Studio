import io
import wave
from typing import List, Tuple, Optional
from .bgm_generator import BGMGenerator


class AudioMixer:
    """
    Assembles multiple speaker dialogue clips into a cohesive podcast episode
    with natural conversational pacing, silence intervals, and background music ducking.
    """

    def __init__(
        self,
        turn_pause_ms: int = 350,
        same_speaker_pause_ms: int = 200,
        intro_pause_ms: int = 400,
        outro_pause_ms: int = 600,
        bgm_style: Optional[str] = "lofi_ambient",
    ):
        self.turn_pause_ms = turn_pause_ms
        self.same_speaker_pause_ms = same_speaker_pause_ms
        self.intro_pause_ms = intro_pause_ms
        self.outro_pause_ms = outro_pause_ms
        self.bgm_style = bgm_style
        self.bgm_generator = BGMGenerator(style=bgm_style) if bgm_style and bgm_style != "none" else None

    def _create_silence(self, duration_ms: int, framerate: int, sampwidth: int, nchannels: int) -> bytes:
        """Generates silent PCM audio frames for a given duration in milliseconds."""
        num_frames = int((framerate * duration_ms) / 1000)
        bytes_per_frame = sampwidth * nchannels
        return b"\x00" * (num_frames * bytes_per_frame)

    def assemble(
        self,
        audio_segments: List[Tuple[str, bytes]],
        output_filepath: str,
        enable_bgm: bool = True,
    ) -> float:
        """
        Combines audio segments (list of (speaker, wav_bytes)) into a single WAV file.
        Optionally mixes background music with ducking and intro/outro jingle.
        Returns total duration in seconds.
        """
        if not audio_segments:
            raise ValueError("No audio segments to assemble.")

        valid_segments = [(speaker, data) for speaker, data in audio_segments if data]
        if not valid_segments:
            raise ValueError("All audio segments are empty.")

        # Read master audio format parameters from the first segment
        first_data = valid_segments[0][1]
        with wave.open(io.BytesIO(first_data), "rb") as ref:
            params = ref.getparams()
            nchannels = ref.getnchannels()
            sampwidth = ref.getsampwidth()
            framerate = ref.getframerate()

        dialogue_pcm_chunks = []
        last_speaker = None

        # Build raw dialogue stream with natural turn pauses
        if self.intro_pause_ms > 0:
            dialogue_pcm_chunks.append(
                self._create_silence(self.intro_pause_ms, framerate, sampwidth, nchannels)
            )

        for i, (speaker, wav_bytes) in enumerate(valid_segments):
            if i > 0:
                pause_ms = (
                    self.same_speaker_pause_ms
                    if speaker == last_speaker
                    else self.turn_pause_ms
                )
                dialogue_pcm_chunks.append(
                    self._create_silence(pause_ms, framerate, sampwidth, nchannels)
                )

            with wave.open(io.BytesIO(wav_bytes), "rb") as seg_wav:
                frames = seg_wav.readframes(seg_wav.getnframes())
                dialogue_pcm_chunks.append(frames)

            last_speaker = speaker

        if self.outro_pause_ms > 0:
            dialogue_pcm_chunks.append(
                self._create_silence(self.outro_pause_ms, framerate, sampwidth, nchannels)
            )

        combined_dialogue_pcm = b"".join(dialogue_pcm_chunks)

        # Mix with background music and ducking if requested
        if enable_bgm and self.bgm_generator:
            final_pcm = self.bgm_generator.mix_dialogue_with_bgm(
                combined_dialogue_pcm,
                framerate=framerate,
                intro_solo_sec=2.2,
                outro_solo_sec=2.8,
                bgm_full_volume=0.22,
                bgm_duck_volume=0.045,
            )
        else:
            final_pcm = combined_dialogue_pcm

        # Write to final WAV file
        with wave.open(output_filepath, "wb") as out_wav:
            out_wav.setparams(params)
            out_wav.writeframes(final_pcm)

        total_frames = len(final_pcm) // (sampwidth * nchannels)
        duration_sec = total_frames / float(framerate)
        return duration_sec
