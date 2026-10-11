# 🎙️ AI Podcast Generator (Powered by Sarvam AI)

An end-to-end AI Podcast production engine built with **Sarvam AI's Indic models**. Converts simple topics, prompts, or reference documents into fully produced multi-speaker audio podcast episodes.

---

## ⚡ Architecture & Sarvam AI Integration

1. **Scriptwriter Engine (`sarvam-105b-conversations`)**:
   - Takes a topic, tone, target language, and optional source document.
   - Generates realistic, natural dialogue between two distinct hosts with banter, hooks, and natural conversational cadence.
2. **Multi-Speaker Voice Synthesis (`bulbul:v3`)**:
   - Turns each dialogue line into expressive audio using Sarvam's natural Indic and Indian-English voices.
   - Built-in speaker mappings for **Rohan**, **Priya**, **Rahul**, **Simran**, **Aayan**, **Kavya**, **Ashutosh**, and more.
3. **Audio Mastering & Pacing**:
   - Concatenates audio segments with conversational pauses (350ms between speaker turns, 200ms within sentences).
   - Generates production-ready `.wav` master audio files.
4. **Episode Transcripts**:
   - Automatically exports formatted `.md` and `.json` transcripts with metadata.

---

## 🚀 How to Run in Terminal

### Interactive Mode:
```powershell
py generate_podcast.py
```
This launches a guided interactive wizard where you can:
- Type your podcast topic or prompt
- Choose language (English, Hindi, Hinglish, etc.)
- Set episode length / dialogue turns
- Provide an optional document/notes file

### Direct CLI Command:
```powershell
py generate_podcast.py --topic "The Future of Electric Vehicles in India" --turns 6
```

With source document notes:
```powershell
py generate_podcast.py --topic "Quarterly Tech Review" --doc notes.txt --turns 8
```

---

## 📁 Project Structure

```
sarvam/
├── .env                  # SARVAM_API_KEY
├── .gitignore            # Ignores .env and audio outputs
├── main.py               # Interactive Sarvam chat CLI
├── generate_podcast.py   # Podcast generator CLI
├── podcast/
│   ├── script_generator.py   # Writes multi-speaker scripts via sarvam-105b
│   ├── voice_synthesizer.py  # Converts script to audio using bulbul:v3
│   ├── audio_mixer.py        # Assembles and times dialogue turns
│   └── pipeline.py           # Orchestrates the complete pipeline
└── output/                   # Generated .wav audio and transcripts
```
