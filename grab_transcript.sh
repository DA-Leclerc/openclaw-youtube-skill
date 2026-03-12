#!/bin/bash
URL="$1"
OUTPUT_DIR="$HOME/transcripts"
TMPDIR="/tmp/yt_audio"
mkdir -p "$OUTPUT_DIR" "$TMPDIR"

TITLE=$(yt-dlp --get-title "$URL" 2>/dev/null | tr ' /' '_' | head -c 60)
OUTFILE="$OUTPUT_DIR/${TITLE}.txt"

echo "Processing: $TITLE"

yt-dlp --write-subs --write-auto-sub --sub-lang en \
  --sub-format srt --convert-subs srt \
  --skip-download -o "$TMPDIR/%(title)s" "$URL" 2>/dev/null

SRT_FILE=$(find "$TMPDIR" -name "*.srt" | head -1)

if [ -n "$SRT_FILE" ]; then
  sed '/^[0-9]*$/d; /^[0-9:,]* --> [0-9:,]*$/d; /^$/d' "$SRT_FILE" > "$OUTFILE"
  echo "Captions method: SUCCESS -> $OUTFILE"
  rm -f "$SRT_FILE"
else
  echo "No captions found. Falling back to Whisper..."
  yt-dlp -x --audio-format mp3 -o "$TMPDIR/audio.mp3" "$URL"
  /home/dominic/.openclaw/whisper-env/bin/whisper "$TMPDIR/audio.mp3" --model base \
    --output_format txt --output_dir "$OUTPUT_DIR"
  mv "$OUTPUT_DIR/audio.txt" "$OUTFILE" 2>/dev/null || true
  rm -f "$TMPDIR/audio.mp3"
  echo "Whisper method: SUCCESS -> $OUTFILE"
fi
