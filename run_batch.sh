#!/bin/bash
CHANNELS=(
  "https://www.youtube.com/@JordiVisserlabs"
  "https://www.youtube.com/@InvestAnswers"
  "https://www.youtube.com/@InvestAnswers/streams"
  "https://www.youtube.com/@peterdiamandis"
  "https://www.youtube.com/@PaulCryptoformation"
  "https://www.youtube.com/@AnthonyPompliano"
)

for channel in "${CHANNELS[@]}"; do
  echo "Fetching latest from: $channel"
  LATEST=$(yt-dlp --playlist-end 1 --get-id "$channel/videos" 2>/dev/null | head -1)
  if [ -n "$LATEST" ]; then
    ~/grab_transcript.sh "https://www.youtube.com/watch?v=$LATEST"
  else
    echo "Could not fetch latest video from $channel"
  fi
  sleep 10
done

cp ~/transcripts/*.txt ~/.openclaw/workspace-james/transcripts/ 2>/dev/null
echo "Batch complete. Transcripts in ~/transcripts/ and James workspace."
