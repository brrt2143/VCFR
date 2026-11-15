#!/usr/bin/env bash
set -euo pipefail

DEMO_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PYTHON="${PYTHON:-python3}"
FFMPEG="${FFMPEG:-ffmpeg}"
FFPROBE="${FFPROBE:-ffprobe}"
VOICE="${VOICE:-es_MX-claude-high}"
MODEL_DIR="$DEMO_DIR/.models"
MODEL="$MODEL_DIR/$VOICE.onnx"
CONFIG="$MODEL.json"
WORK_DIR="$(mktemp -d)"
trap 'rm -rf "$WORK_DIR"' EXIT

command -v "$PYTHON" >/dev/null || { echo "Python 3 is required." >&2; exit 1; }
command -v "$FFMPEG" >/dev/null || { echo "FFmpeg is required." >&2; exit 1; }
command -v "$FFPROBE" >/dev/null || { echo "FFprobe is required." >&2; exit 1; }
"$PYTHON" -c 'import piper' >/dev/null 2>&1 || {
  echo 'Install the Piper engine first: python3 -m pip install piper-tts' >&2
  exit 1
}

mkdir -p "$MODEL_DIR"
if [[ ! -s "$MODEL" || ! -s "$CONFIG" ]]; then
  "$PYTHON" -m piper.download_voices --download-dir "$MODEL_DIR" "$VOICE"
fi

"$PYTHON" -m piper \
  --model "$MODEL" \
  --config "$CONFIG" \
  --input-file "$DEMO_DIR/narration-es.txt" \
  --output-file "$WORK_DIR/narration.wav" \
  --length-scale 1.08 \
  --sentence-silence 0.30 \
  --data-dir "$MODEL_DIR"

AUDIO_SECONDS="$("$FFPROBE" -v error -show_entries format=duration -of csv=p=0 "$WORK_DIR/narration.wav")"
LAST_SECONDS="$("$PYTHON" -c 'import sys; print(max(5.04, float(sys.argv[1]) - 30 + 0.04))' "$AUDIO_SECONDS")"

INPUTS=()
FILTER=""
for index in 1 2 3 4 5 6 7; do
  printf -v scene '%02d' "$index"
  duration=5
  if [[ "$index" == 7 ]]; then duration="$LAST_SECONDS"; fi
  INPUTS+=( -loop 1 -framerate 25 -t "$duration" -i "$DEMO_DIR/frames/scene-$scene.png" )
  FILTER+="[$((index - 1)):v]fps=25,setsar=1,format=yuv420p[v$index];"
done
FILTER+="[v1][v2][v3][v4][v5][v6][v7]concat=n=7:v=1:a=0[vout]"

"$FFMPEG" -hide_banner -y \
  "${INPUTS[@]}" \
  -i "$WORK_DIR/narration.wav" \
  -filter_complex "$FILTER" \
  -map '[vout]' -map '7:a:0' \
  -t "$AUDIO_SECONDS" \
  -c:v libx264 -preset medium -crf 22 -pix_fmt yuv420p \
  -c:a aac -b:a 128k -ar 22050 -ac 1 -movflags +faststart \
  "$DEMO_DIR/VCFR-Demo.mp4"

echo "Created $DEMO_DIR/VCFR-Demo.mp4 with voice $VOICE"
