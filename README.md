# openclaw-youtube-skill

A hybrid YouTube transcript pipeline for [OpenClaw](https://openclaw.ai) agents.

Fetches transcripts using **YouTube captions first** (fast, no CPU cost), and automatically falls back to **local Whisper transcription** if captions are unavailable — including for non-English channels.

---

## What's Included

| File | Purpose |
|------|---------|
| `grab_transcript.sh` | Fetches a single YouTube URL and saves transcript to `~/transcripts/` |
| `run_batch.sh` | Nightly batch runner — pulls latest video from a list of channels |
| `skill/youtube.py` | OpenClaw agent skill — drop into any agent's skills folder |
| `skill/youtube.yaml` | Skill manifest for OpenClaw |

---

## Prerequisites

**yt-dlp**
```bash
pip install yt-dlp
```

**Whisper** (for the fallback — skip if your channels always have captions)
```bash
python3 -m venv ~/.openclaw/whisper-env
source ~/.openclaw/whisper-env/bin/activate
pip install openai-whisper
```

> The default Whisper path is `~/.openclaw/whisper-env/bin/whisper`.
> Override with the `WHISPER_BIN` environment variable if yours is elsewhere.

---

## Setup

### 1. Install the scripts
```bash
cp grab_transcript.sh ~/grab_transcript.sh
cp run_batch.sh ~/run_batch.sh
chmod +x ~/grab_transcript.sh ~/run_batch.sh
mkdir -p ~/transcripts
```

### 2. Configure your channels

Edit `~/run_batch.sh` and add your YouTube channel URLs to the `CHANNELS` array:
```bash
CHANNELS=(
  "https://www.youtube.com/@YourChannel1"
  "https://www.youtube.com/@YourChannel2"
  "https://www.youtube.com/@YourChannel3/streams"  # for livestream archives
)
```

Also set `AGENT_WORKSPACE` to the transcripts folder your agent reads from:
```bash
AGENT_WORKSPACE="$HOME/.openclaw/workspace-james/transcripts"
```

### 3. Install the agent skill
```bash
cp skill/youtube.py ~/.openclaw/agents/james/agent/skills/youtube.py
cp skill/youtube.yaml ~/.openclaw/agents/james/agent/skills/youtube.yaml
```

Then add a note to that agent's `SOUL.md`:
```markdown
## YouTube Skill
You have access to a `youtube` skill that fetches full transcripts from any
YouTube URL. Use it whenever the user shares a YouTube link.

Example: `use_skill("youtube", {"url": "https://youtu.be/VIDEO_ID"})`

The skill tries captions first, then falls back to Whisper if needed.
```

### 4. Set up the nightly cron
```bash
crontab -e
```
```
# 4AM: pull latest transcripts from all channels
0 4 * * * /home/youruser/run_batch.sh >> /home/youruser/transcript_log.txt 2>&1
```

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `WHISPER_BIN` | `~/.openclaw/whisper-env/bin/whisper` | Path to Whisper binary |
| `WHISPER_MODEL` | `base` | Whisper model size (`tiny`, `base`, `small`, `medium`, `large`) |
| `TRANSCRIPT_OUTPUT_DIR` | `~/transcripts` | Where transcript `.txt` files are saved |
| `AGENT_WORKSPACE` | `~/.openclaw/workspace-james/transcripts` | Where `run_batch.sh` copies files for the agent |

---

## Whisper Model Guide

| Model | Speed | VRAM | Notes |
|-------|-------|------|-------|
| `tiny` | Fastest | ~1GB | Good for quick summaries, lower accuracy |
| `base` | Fast | ~1GB | **Recommended default** — multilingual, solid accuracy |
| `small` | Moderate | ~2GB | Better accuracy for non-English |
| `medium` | Slow | ~5GB | High accuracy |
| `large` | Slowest | ~10GB | Best quality |

`base` is multilingual by default — it will auto-detect and transcribe French, Spanish, etc.

---

## How It Works
```
grab_transcript.sh <url>
  │
  ├─ yt-dlp: download .srt captions
  │     └─ SUCCESS → strip formatting → save .txt ✓
  │
  └─ NO CAPTIONS FOUND
        └─ yt-dlp: download audio as .mp3
              └─ Whisper: transcribe → save .txt ✓
```

The agent skill (`youtube.py`) wraps this script, adds JSON I/O for OpenClaw, caches results in `/tmp/openclaw_yt_cache/`, and returns metadata alongside the transcript.

---

## Example Agent Cron Job
```json
{
  "name": "james-youtube-investment-report",
  "schedule": { "expr": "0 7 * * *", "tz": "America/Toronto" },
  "enabled": true,
  "payload": {
    "timeoutSeconds": 180,
    "message": "Read all .txt files in transcripts/ modified in the last 24 hours. Extract investment ideas and produce a one-page report with: TOP CALLS / KEY THEMES / RISKS TO WATCH / SOURCE SUMMARY. Max 400 words. Send via Telegram."
  }
}
```

---

## License

MIT

