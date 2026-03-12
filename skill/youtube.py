#!/usr/bin/env python3
import sys, json, re, subprocess, argparse
from pathlib import Path
from datetime import datetime

def extract_video_id(url):
    m = re.search(r"(?:v=|youtu\.be/|embed/|shorts/)([A-Za-z0-9_-]{11})", url)
    return m.group(1) if m else None

def get_metadata(video_id):
    try:
        r = subprocess.run(["yt-dlp","--dump-json","--no-download",
                            f"https://www.youtube.com/watch?v={video_id}"],
                           capture_output=True, text=True, timeout=30)
        if r.returncode == 0:
            d = json.loads(r.stdout)
            return {"title": d.get("title",""), "channel": d.get("uploader",""),
                    "upload_date": d.get("upload_date",""), "duration": d.get("duration",0)}
    except: pass
    return {}

def main():
    payload = {}
    if not sys.stdin.isatty():
        try: payload = json.load(sys.stdin)
        except: pass
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default=payload.get("url",""))
    parser.add_argument("--format", default=payload.get("format","clean"),
                        choices=["clean","raw","timestamped"])
    args = parser.parse_args()

    if not args.url:
        print(json.dumps({"error": "No URL provided"})); sys.exit(1)

    video_id = extract_video_id(args.url)
    if not video_id:
        print(json.dumps({"error": f"Could not extract video ID from: {args.url}"})); sys.exit(1)

    # Check cache first
    cache_dir = Path("/tmp/james_transcripts")
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_file = cache_dir / f"{video_id}_{args.format}.json"
    if cache_file.exists():
        result = json.loads(cache_file.read_text())
        result["cached"] = True
        print(json.dumps(result, ensure_ascii=False))
        return

    # Run hybrid grab script
    import time
    transcripts_dir = Path.home() / "transcripts"
    before_time = time.time()

    r = subprocess.run(
        [str(Path.home() / "grab_transcript.sh"),
         f"https://www.youtube.com/watch?v={video_id}"],
        capture_output=True, text=True
    )

    time.sleep(1)

    # Find most recently modified txt file after run
    txt_files = list(transcripts_dir.glob("*.txt"))
    new_files = [f for f in txt_files if f.stat().st_mtime >= before_time]

    result = {
        "video_id": video_id,
        "url": args.url,
        "cached": False,
        "metadata": get_metadata(video_id),
        "fetched_at": datetime.now().isoformat() + "Z"
    }

    if not new_files:
        result["error"] = "No transcript file created by hybrid script"
        print(json.dumps(result, ensure_ascii=False))
        sys.exit(1)

    transcript_file = sorted(new_files, key=lambda f: f.stat().st_mtime)[-1]
    text = transcript_file.read_text().strip()
    text = re.sub(r"\s+", " ", text)

    result.update({
        "transcript_source": "hybrid (captions or whisper)",
        "transcript": text,
        "word_count": len(text.split())
    })

    cache_file.write_text(json.dumps(result, ensure_ascii=False))
    print(json.dumps(result, ensure_ascii=False))

if __name__ == "__main__": main()
