# 🎙️ Sarvam Studio — AI Multi-Speaker Podcast Generator

> An end-to-end AI Podcast production engine built with **Sarvam AI's Indic models**. Converts simple topics, prompts, or research documents into fully produced multi-speaker audio podcast episodes complete with **expressive voices, acoustic background music ducking, and synchronized transcripts**.

[![GitHub Repo](https://img.shields.io/badge/GitHub-Repository-blue?logo=github)](https://github.com/Iitian-shivansh/Sarvam-Studio)
[![Powered by Sarvam AI](https://img.shields.io/badge/Powered%20by-Sarvam%20AI-orange)](https://docs.sarvam.ai)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-green?logo=fastapi)](https://fastapi.tiangolo.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-purple.svg)](https://opensource.org/licenses/MIT)

---

## 🌟 Key Features

- **🧠 Autonomous Two-Host Scriptwriting (`sarvam-105b-conversations`)**  
  Generates dynamic, hyper-realistic banter between two distinct host personas (Host 1: curious inquisitor, Host 2: expert storyteller) with hooks, pauses, and natural chemistry.
- **🗣️ Natural Indic & English Voice Synthesis (`bulbul:v3`)**  
  Uses Sarvam's conversational voices (`rohan`, `priya`, `aayan`, `kavya`, `rahul`, `simran`, `ashutosh`, etc.) with nuanced pacing, pitch, and emotion.
- **📄 Document Research & Grounding (PDF / TXT / MD)**  
  Drop in research papers, company memos, or articles. Sarvam extracts key talking points, data highlights, and debate angles to ground the podcast in real content.
- **🎵 Procedural Background Music & Acoustic Ducking**  
  Blends custom or procedural ambient background music (`Lo-Fi Ambient`, `Tech Upbeat`, `Cinematic News`) with an intro jingle, ducking down during speech so dialogue remains crystal-clear, and swelling for the outro.
- **💻 Modern Dark Studio Web UI**  
  FastAPI + Vanilla CSS/JS single-page web dashboard featuring an interactive waveform audio player, speed controls, synchronized dialogue transcript cards, and one-click episode exports (`.wav` & `.md`).
- **⌨️ Interactive Terminal CLI**  
  Prefer the command line? Run the full interactive production wizard right inside your terminal with real-time streaming logs.

---

## ⚡ Architecture & Sarvam Models

```text
[Topic Prompt or Uploaded PDF/Document]
                 │
                 ▼
┌────────────────────────────────────────────────────────┐
│ 1. Document Extraction & Research                      │
│    - pypdf + Sarvam-105B key insight extraction        │
└────────────────────────────────────────────────────────┘
                 │
                 ▼
┌────────────────────────────────────────────────────────┐
│ 2. Scriptwriting Engine                                │
│    - Model: sarvam-105b-conversations                  │
│    - Outputs structured multi-speaker dialogue JSON    │
└────────────────────────────────────────────────────────┘
                 │
                 ▼
┌────────────────────────────────────────────────────────┐
│ 3. Multi-Speaker Voice Synthesis                       │
│    - Model: bulbul:v3 (Indian English & Indic voices)  │
│    - Generates 16-bit 22.05kHz PCM audio clips         │
└────────────────────────────────────────────────────────┘
                 │
                 ▼
┌────────────────────────────────────────────────────────┐
│ 4. Mastering & Acoustic Ducking Engine                 │
│    - Natural turn buffers (350ms between speakers)     │
│    - Dynamic BGM ducking (solo intro -> ducked dialogue│
│      -> outro swell)                                   │
└────────────────────────────────────────────────────────┘
                 │
                 ▼
┌────────────────────────────────────────────────────────┐
│ 5. Master Output Delivery                              │
│    - Audio: .wav file                                  │
│    - Transcripts: .md & .json metadata                 │
│    - Real-time Web Dashboard & Terminal CLI Player     │
└────────────────────────────────────────────────────────┘
```

---

## 🚀 Quickstart Guide

### 1. Clone & Install Dependencies
```bash
git clone https://github.com/Iitian-shivansh/Sarvam-Studio.git
cd Sarvam-Studio
pip install -r requirements.txt
```

### 2. Configure Your API Key
Create a `.env` file in the project root:
```env
SARVAM_API_KEY=your_sarvam_api_key_here
```
*(Get your key at [dashboard.sarvam.ai](https://dashboard.sarvam.ai))*

---

## 🎮 Running the Application

### Option A: Launch the Web Studio Dashboard
```bash
py server.py
# or: uvicorn server:app --reload
```
Open **`http://127.0.0.1:8000`** in your browser. You can:
- Select topics or drag-and-drop a PDF.
- Customize host voices, language, and background music.
- Play generated episodes with interactive transcripts and download master audio.

### Option B: Terminal CLI Production Wizard
```bash
# Interactive guided mode
py generate_podcast.py

# One-line generation with flags
py generate_podcast.py --topic "Future of UPI & Global Payments" --bgm lofi_ambient --turns 6

# Generate directly from a document
py generate_podcast.py --topic "EV Industry Analysis" --doc report.pdf --turns 8
```

### Option C: Terminal Chat with Sarvam-105B
```bash
py main.py
```

---

## 📁 Repository Structure

```
Sarvam-Studio/
├── podcast/
│   ├── script_generator.py    # Researches & writes 2-host scripts (sarvam-105b)
│   ├── voice_synthesizer.py   # Synthesizes dialogue turns (bulbul:v3)
│   ├── bgm_generator.py       # Procedural BGM & acoustic volume ducking
│   ├── document_parser.py     # PDF & document extraction
│   ├── audio_mixer.py         # Assembles dialogue, pauses, and music
│   └── pipeline.py            # End-to-end pipeline orchestrator
├── web/
│   ├── index.html             # Studio single-page application
│   ├── style.css              # Dark glassmorphic design system
│   └── app.js                 # Player, waveforms & API client
├── server.py                  # FastAPI backend server
├── generate_podcast.py        # Terminal CLI generator
├── main.py                    # Terminal conversational assistant
├── requirements.txt           # Pinned dependencies
├── .env.example               # Template environment variables
└── README.md                  # Project documentation
```

---

## 🛡️ License
MIT License. Built with ❤️ powered by [Sarvam AI](https://sarvam.ai).
