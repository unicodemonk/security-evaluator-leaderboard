#!/bin/bash
# 🎬 Create 3-Minute Video WITHOUT ffmpeg text overlays
# Uses simple slideshow with pre-rendered images

set -e

AUDIO_DIR="$HOME/Desktop/demo-recordings/voiceover-3min"
OUTPUT_DIR="$HOME/Desktop/demo-recordings/final"
FRAMES_DIR="$OUTPUT_DIR/frames-simple"

mkdir -p "$FRAMES_DIR"

echo "🎬 Creating 3-Minute Demo Video (Simplified)"
echo "============================================="
echo ""

# Step 1: Combine audio
echo "🎵 Step 1: Combining audio files..."
cd "$AUDIO_DIR"

cat > combine-list.txt << 'EOF'
file 'scene1-intro.wav'
file 'scene2-leaderboard.wav'
file 'scene3-socbench.wav'
file 'scene4-homeauto.wav'
file 'scene5-law.wav'
file 'scene6-mitre.wav'
file 'scene7-reports.wav'
file 'scene8-github.wav'
file 'scene9-submit.wav'
file 'scene10-cta.wav'
EOF

# Use afconvert (built-in macOS) to concatenate
echo "  Combining with macOS tools..."
cd "$AUDIO_DIR"
cat scene*.wav > "$OUTPUT_DIR/combined-temp.wav" 2>/dev/null || {
    # If simple concat doesn't work, use afconvert
    afconvert scene1-intro.wav -d LEI16 -f WAVE "$OUTPUT_DIR/part1.wav"
    afconvert scene2-leaderboard.wav -d LEI16 -f WAVE "$OUTPUT_DIR/part2.wav"
    afconvert scene3-socbench.wav -d LEI16 -f WAVE "$OUTPUT_DIR/part3.wav"
    afconvert scene4-homeauto.wav -d LEI16 -f WAVE "$OUTPUT_DIR/part4.wav"
    afconvert scene5-law.wav -d LEI16 -f WAVE "$OUTPUT_DIR/part5.wav"
    afconvert scene6-mitre.wav -d LEI16 -f WAVE "$OUTPUT_DIR/part6.wav"
    afconvert scene7-reports.wav -d LEI16 -f WAVE "$OUTPUT_DIR/part7.wav"
    afconvert scene8-github.wav -d LEI16 -f WAVE "$OUTPUT_DIR/part8.wav"
    afconvert scene9-submit.wav -d LEI16 -f WAVE "$OUTPUT_DIR/part9.wav"
    afconvert scene10-cta.wav -d LEI16 -f WAVE "$OUTPUT_DIR/part10.wav"
}

echo "✅ Audio ready"
echo ""

# Step 2: Create simple colored slides using macOS screencapture
echo "🎨 Step 2: Creating video slides..."
echo "  Opening demo HTML page for screenshot..."

# Open the demo page
open "/Users/arch/Documents/SecEval6/security-evaluator-leaderboard/demo_video/index.html"

sleep 3

echo ""
echo "📸 Taking screenshots of demo page..."
echo "   (Screenshots will capture the open browser window)"

# Take a screenshot of the full screen
screencapture -x "$FRAMES_DIR/demo-screenshot.png"

echo "✅ Screenshot captured"
echo ""

# Step 3: Play audio
echo "🔊 Step 3: Playing complete audio..."
echo "  (This is your 3-minute voiceover)"
echo ""

# Play all audio files in sequence
for i in {1..10}; do
    wavfile=$(ls "$AUDIO_DIR"/scene${i}*.wav 2>/dev/null | head -1)
    if [ -f "$wavfile" ]; then
        echo "  ▶️  Playing: $(basename "$wavfile")"
        afplay "$wavfile"
    fi
done

echo ""
echo "✅ Audio playback complete!"
echo ""

echo "📹 NEXT STEPS - Create Final Video:"
echo "==================================="
echo ""
echo "You have two options:"
echo ""
echo "Option A: Wait for ffmpeg-full to finish installing, then run:"
echo "   ./create-video-3min.sh"
echo ""
echo "Option B: Manual screen recording (5 minutes):"
echo "   1. Open: /Users/arch/Documents/SecEval6/security-evaluator-leaderboard/demo_video/index.html"
echo "   2. Press Cmd+Shift+5 to start screen recording"
echo "   3. Run this script again to play audio"
echo "   4. Navigate through demo while audio plays"
echo "   5. Save recording as: ~/Desktop/demo-recordings/demo-final.mov"
echo ""
echo "📁 Files ready:"
echo "   Audio: $AUDIO_DIR/scene*.wav (10 files, ~86 seconds)"
echo "   Screenshot: $FRAMES_DIR/demo-screenshot.png"
echo ""
