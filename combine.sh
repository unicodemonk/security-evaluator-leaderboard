#!/bin/bash
VIDEO_PATH="/Users/arch/Documents/SecEval6/security-evaluator-leaderboard/demo_video.webp"
AUDIO_DIR="/Users/arch/Documents/SecEval6/SecurityEvaluator"
OUTPUT_PATH="/Users/arch/Documents/SecEval6/security-evaluator-leaderboard/final_demo.mp4"

echo "Combining video and audio..."

/opt/homebrew/bin/ffmpeg -y \
-i "$VIDEO_PATH" \
-i "$AUDIO_DIR/audio_01_intro.aiff" \
-i "$AUDIO_DIR/audio_02_leaderboard.aiff" \
-i "$AUDIO_DIR/audio_03_comparison.aiff" \
-i "$AUDIO_DIR/audio_04_how_it_works.aiff" \
-i "$AUDIO_DIR/audio_05_socbench.aiff" \
-i "$AUDIO_DIR/audio_06_homeauto.aiff" \
-i "$AUDIO_DIR/audio_07_law.aiff" \
-i "$AUDIO_DIR/audio_08_mitre.aiff" \
-i "$AUDIO_DIR/audio_09_github.aiff" \
-i "$AUDIO_DIR/audio_10_submit.aiff" \
-i "$AUDIO_DIR/audio_11_outro.aiff" \
-filter_complex "
[1]adelay=0|0[a1];
[2]adelay=12000|12000[a2];
[3]adelay=30000|30000[a3];
[4]adelay=45000|45000[a4];
[5]adelay=60000|60000[a5];
[6]adelay=90000|90000[a6];
[7]adelay=120000|120000[a7];
[8]adelay=165000|165000[a8];
[9]adelay=180000|180000[a9];
[10]adelay=210000|210000[a10];
[11]adelay=250000|250000[a11];
[a1][a2][a3][a4][a5][a6][a7][a8][a9][a10][a11]amix=inputs=11:dropout_transition=0[aout]
" \
-map 0:v -map "[aout]" \
-c:v libx264 -pix_fmt yuv420p \
-c:a aac -b:a 192k \
"$OUTPUT_PATH"

echo "Done! Saved to $OUTPUT_PATH"
