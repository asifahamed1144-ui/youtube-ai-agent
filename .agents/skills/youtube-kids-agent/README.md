# 🎬 Self-Learning YouTube AI Agent

This repository powers a fully autonomous YouTube Shorts generation system.

## 🚀 What it does

Every run, the system:
- Learns from past video performance (memory.json)
- Generates a viral kids video idea
- Creates story, scenes, and image prompts
- Generates AI voice narration
- Builds a complete video (MP4)
- Updates its memory for self-improvement

---

## 🧠 Self-Learning Loop

The system improves over time by:
- Tracking predicted viral scores
- Storing video performance history
- Adjusting future content strategy automatically

---

## 📁 Files

- `memory.json` → stores learning history
- `main.py` → full AI agent pipeline
- `README.md` → project overview
- `schema.md` → memory structure definition

---

## ⚙️ Requirements

Install dependencies:

```bash
pip install openai requests moviepy pillow google-api-python-client google-auth google-auth-oauthlib google-auth-httplib2
