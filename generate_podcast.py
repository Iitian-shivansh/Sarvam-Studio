import argparse
import os
import sys
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("SARVAM_API_KEY")
if not api_key:
    print("[Error] SARVAM_API_KEY not found in .env. Please add it first.")
    sys.exit(1)

from podcast.pipeline import PodcastPipeline
from podcast.voice_synthesizer import AVAILABLE_VOICES


def print_banner():
    print("=" * 65)
    print("      🎙️  SARVAM AI PODCAST GENERATOR (Multi-Speaker)  🎙️")
    print("=" * 65)
    print(" Powered by Sarvam-105B (Scriptwriting) & Bulbul v3 (Voice Synthesis)")
    print("=" * 65 + "\n")


def interactive_mode():
    print_banner()

    topic = input("Enter podcast topic or prompt: ").strip()
    if not topic:
        topic = "The Rise of Quick Commerce in India: Convenience vs Cost"
        print(f"Using default topic: '{topic}'")

    print("\nSupported Languages:")
    print("  1. English (en-IN) [Default]")
    print("  2. Hindi (hi-IN)")
    print("  3. Hinglish (en-IN with Hindi conversational context)")
    lang_choice = input("Select language [1/2/3] (default 1): ").strip()

    if lang_choice == "2":
        language = "Hindi"
        language_code = "hi-IN"
        host_1 = ("Aayan", "aayan")
        host_2 = ("Kavya", "kavya")
    elif lang_choice == "3":
        language = "Hinglish (Hindi-English mix)"
        language_code = "en-IN"
        host_1 = ("Rohan", "rohan")
        host_2 = ("Priya", "priya")
    else:
        language = "English"
        language_code = "en-IN"
        host_1 = ("Rohan", "rohan")
        host_2 = ("Priya", "priya")

    print(f"\nHosts: {host_1[0]} (Voice: {host_1[1]}) & {host_2[0]} (Voice: {host_2[1]})")

    turns_input = input("Number of dialogue turns [default 6]: ").strip()
    try:
        num_turns = int(turns_input) if turns_input else 6
    except ValueError:
        num_turns = 6

    print("\nBackground Music & Jingle Style:")
    print("  1. Lo-Fi Ambient (Warm chords & acoustic ducking) [Default]")
    print("  2. Tech Upbeat (Modern arpeggios)")
    print("  3. Cinematic Calm (Deep broadcast pad)")
    print("  4. None (Clean dialogue only)")
    bgm_choice = input("Select BGM [1/2/3/4] (default 1): ").strip()
    bgm_style_map = {"1": "lofi_ambient", "2": "tech_upbeat", "3": "news_calm", "4": "none"}
    bgm_style = bgm_style_map.get(bgm_choice, "lofi_ambient")

    doc_path = input("Optional: path to PDF / text document (press Enter to skip): ").strip()
    if doc_path and not os.path.exists(doc_path):
        print(f"Warning: File {doc_path} not found. Proceeding with prompt only.")
        doc_path = None

    print("\n" + "-" * 50)
    print("Starting generation pipeline...")
    print("-" * 50 + "\n")

    pipeline = PodcastPipeline(
        language_code=language_code,
        host_1_name=host_1[0],
        host_1_voice=host_1[1],
        host_2_name=host_2[0],
        host_2_voice=host_2[1],
        bgm_style=bgm_style,
    )

    def on_progress(msg: str, current: int, total: int):
        if total > 0:
            print(f"[{current}/{total}] {msg}")
        else:
            print(f"[*] {msg}")

    result = pipeline.generate_episode(
        topic=topic,
        output_dir="output",
        document_path=doc_path,
        num_turns=num_turns,
        language=language,
        enable_bgm=(bgm_style != "none"),
        progress_callback=on_progress,
    )

    print("\n" + "=" * 65)
    print("🎉 PODCAST EPISODE READY!")
    print("=" * 65)
    print(f"Topic:       {result['topic']}")
    print(f"Duration:    {result['duration_formatted']}")
    print(f"Audio File:  {result['audio_path']}")
    print(f"Transcript:  {result['transcript_md']}")
    print("=" * 65 + "\n")

    print("--- PREVIEW TRANSCRIPT ---")
    for turn in result["script"]:
        print(f"\n{turn['speaker']}:")
        print(f"  \"{turn['text']}\"")
    print("\n" + "=" * 65)


def main():
    parser = argparse.ArgumentParser(description="Generate multi-speaker podcast episodes using Sarvam AI")
    parser.add_argument("--topic", type=str, help="Topic for the podcast")
    parser.add_argument("--turns", type=int, default=6, help="Number of dialogue turns")
    parser.add_argument("--lang", type=str, default="en-IN", help="Language code (en-IN, hi-IN, etc.)")
    parser.add_argument("--doc", type=str, help="Path to PDF / text document")
    parser.add_argument("--bgm", type=str, default="lofi_ambient", help="BGM style: lofi_ambient, tech_upbeat, news_calm, none")
    args = parser.parse_args()

    if args.topic:
        pipeline = PodcastPipeline(language_code=args.lang, bgm_style=args.bgm)
        result = pipeline.generate_episode(
            topic=args.topic,
            num_turns=args.turns,
            document_path=args.doc if args.doc and os.path.exists(args.doc) else None,
            enable_bgm=(args.bgm != "none"),
            progress_callback=lambda msg, c, t: print(f"[{c}/{t}] {msg}"),
        )
        print(f"\nAudio generated: {result['audio_path']}")
    else:
        interactive_mode()


if __name__ == "__main__":
    main()
