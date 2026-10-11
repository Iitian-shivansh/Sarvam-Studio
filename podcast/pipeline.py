import json
import os
import time
from typing import Callable, Dict, List, Optional, Any
from sarvamai import SarvamAI

from .script_generator import PodcastScriptGenerator
from .voice_synthesizer import VoiceSynthesizer, AVAILABLE_VOICES
from .audio_mixer import AudioMixer
from .document_parser import DocumentParser


class PodcastPipeline:
    """
    End-to-End AI Podcast Generator:
    Topic / Document -> Script Generation -> Multi-Speaker Voice Synthesis -> BGM Ducking & Assembly
    """

    def __init__(
        self,
        client: Optional[SarvamAI] = None,
        language_code: str = "en-IN",
        host_1_name: str = "Rohan",
        host_1_voice: str = "rohan",
        host_2_name: str = "Priya",
        host_2_voice: str = "priya",
        turn_pause_ms: int = 350,
        bgm_style: Optional[str] = "lofi_ambient",
    ):
        self.client = client or SarvamAI()
        self.language_code = language_code
        self.host_1_name = host_1_name
        self.host_2_name = host_2_name
        self.host_1_voice = host_1_voice
        self.host_2_voice = host_2_voice
        self.bgm_style = bgm_style

        self.script_generator = PodcastScriptGenerator(client=self.client)
        self.document_parser = DocumentParser(client=self.client)
        self.voice_synthesizer = VoiceSynthesizer(
            client=self.client,
            language_code=self.language_code,
            speaker_mapping={
                host_1_name.lower(): host_1_voice,
                host_2_name.lower(): host_2_voice,
            },
        )
        self.audio_mixer = AudioMixer(
            turn_pause_ms=turn_pause_ms,
            bgm_style=bgm_style,
        )

    def generate_episode(
        self,
        topic: str,
        output_dir: str = "output",
        document_path: Optional[str] = None,
        source_text: Optional[str] = None,
        num_turns: int = 8,
        language: str = "English",
        tone: str = "conversational, engaging, and lively",
        enable_bgm: bool = True,
        progress_callback: Optional[Callable[[str, int, int], None]] = None,
    ) -> Dict[str, Any]:
        """
        Runs the full end-to-end pipeline to create a podcast episode.
        """
        os.makedirs(output_dir, exist_ok=True)
        timestamp = int(time.time())
        clean_topic = "".join(c if c.isalnum() else "_" for c in topic[:30]).strip("_") or "episode"
        base_name = f"podcast_{clean_topic}_{timestamp}"

        audio_output_path = os.path.join(output_dir, f"{base_name}.wav")
        transcript_json_path = os.path.join(output_dir, f"{base_name}_transcript.json")
        transcript_md_path = os.path.join(output_dir, f"{base_name}_transcript.md")

        def report(msg: str, current: int = 0, total: int = 0):
            if progress_callback:
                progress_callback(msg, current, total)

        doc_meta = None
        combined_source = source_text or ""

        # Step 1: Parse Document if provided
        if document_path and os.path.exists(document_path):
            report(f"Reading document: {os.path.basename(document_path)}...", 0, num_turns)
            parsed_doc = self.document_parser.parse_file(document_path)
            doc_meta = {
                "filename": os.path.basename(document_path),
                "title": parsed_doc["title"],
                "file_type": parsed_doc["file_type"],
                "page_count": parsed_doc.get("page_count", 1),
            }
            report("Analyzing key talking points from document...", 0, num_turns)
            talking_points = self.document_parser.extract_podcast_talking_points(
                parsed_doc["text"], topic_hint=topic
            )
            combined_source = f"{parsed_doc['text']}\n\nKEY TALKING POINTS:\n{talking_points}"

        # Step 2: Script Generation
        report("Writing dialogue script with Sarvam-105B...", 0, num_turns)
        script = self.script_generator.generate(
            topic=topic,
            source_text=combined_source if combined_source else None,
            language=language,
            num_turns=num_turns,
            host_1_name=self.host_1_name,
            host_2_name=self.host_2_name,
            tone=tone,
        )

        total_lines = len(script)
        report(f"Script crafted ({total_lines} dialogue lines). Starting voice synthesis...", 0, total_lines)

        # Step 3: Voice Synthesis
        audio_segments = []
        for i, turn in enumerate(script, 1):
            speaker = turn["speaker"]
            text = turn["text"]
            voice = self.voice_synthesizer.get_voice_for_speaker(speaker)

            report(f"Voicing [{speaker} ({voice})]: \"{text[:45]}...\"", i, total_lines)
            wav_bytes = self.voice_synthesizer.synthesize_line(text, speaker)
            audio_segments.append((speaker, wav_bytes))

        # Step 4: Audio Assembly & BGM Ducking
        bgm_msg = "with background music and ducking" if enable_bgm and self.bgm_style != "none" else "dialogue track"
        report(f"Mastering audio {bgm_msg}...", total_lines, total_lines)
        duration_sec = self.audio_mixer.assemble(
            audio_segments, audio_output_path, enable_bgm=enable_bgm
        )

        # Step 5: Save Transcripts
        with open(transcript_json_path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "topic": topic,
                    "language": language,
                    "duration_seconds": round(duration_sec, 2),
                    "hosts": {
                        self.host_1_name: self.host_1_voice,
                        self.host_2_name: self.host_2_voice,
                    },
                    "document": doc_meta,
                    "bgm_style": self.bgm_style if enable_bgm else None,
                    "script": script,
                },
                f,
                indent=2,
                ensure_ascii=False,
            )

        with open(transcript_md_path, "w", encoding="utf-8") as f:
            f.write(f"# Podcast Episode: {topic}\n\n")
            f.write(f"- **Duration:** {duration_sec:.1f} seconds\n")
            f.write(f"- **Hosts:** {self.host_1_name} ({self.host_1_voice}), {self.host_2_name} ({self.host_2_voice})\n")
            if doc_meta:
                f.write(f"- **Source Document:** {doc_meta['filename']} ({doc_meta['page_count']} pages)\n")
            if enable_bgm and self.bgm_style:
                f.write(f"- **Audio Style:** {self.bgm_style.replace('_', ' ').title()} with dynamic ducking\n")
            f.write("\n## Episode Transcript\n\n")
            for turn in script:
                f.write(f"**{turn['speaker']}**: {turn['text']}\n\n")

        minutes = int(duration_sec // 60)
        seconds = int(duration_sec % 60)
        report(f"Episode ready! Duration: {minutes}m {seconds}s", total_lines, total_lines)

        return {
            "topic": topic,
            "duration_seconds": round(duration_sec, 2),
            "duration_formatted": f"{minutes}m {seconds}s",
            "audio_path": audio_output_path,
            "audio_filename": os.path.basename(audio_output_path),
            "transcript_json": transcript_json_path,
            "transcript_md": transcript_md_path,
            "document": doc_meta,
            "script": script,
        }
