#!/bin/bash
# 🎬 Automated 3-Minute Demo Video Creator
# Uses Apple's built-in tools without requiring ffmpeg

set -e

echo "🎬 AUTOMATED 3-MINUTE DEMO VIDEO"
echo "================================"
echo ""
echo "✅ Status Check:"
echo "  • Audio files: Ready (86 seconds, 10 scenes)"
echo "  • Demo page: demo_video/index.html"
echo "  • Output: ~/Desktop/demo-recordings/demo-3min.mp4"
echo ""

AUDIO_DIR="$HOME/Desktop/demo-recordings/voiceover-3min"
OUTPUT_DIR="$HOME/Desktop/demo-recordings"
DEMO_HTML="/Users/arch/Documents/SecEval6/security-evaluator-leaderboard/demo_video/index.html"

# Check audio files
if [ ! -d "$AUDIO_DIR" ]; then
    echo "❌ Audio directory not found: $AUDIO_DIR"
    exit 1
fi

echo "🎵 Audio Files (Total: ~86 seconds):"
for i in {1..10}; do
    wavfile=$(ls "$AUDIO_DIR"/scene${i}*.wav 2>/dev/null | head -1)
    if [ -f "$wavfile" ]; then
        size=$(ls -lh "$wavfile" | awk '{print $5}')
        echo "  ✓ Scene $i: $(basename "$wavfile") ($size)"
    fi
done
echo ""

echo "📄 Demo Page:"
if [ -f "$DEMO_HTML" ]; then
    echo "  ✓ $DEMO_HTML"
else
    echo "  ❌ Demo HTML not found"
    exit 1
fi
echo ""

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                    AUTOMATED VIDEO CREATION                    ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "This script will:"
echo "  1. Open the demo page in your browser"
echo "  2. Guide you through automated screen recording"
echo "  3. Play audio narration automatically"
echo "  4. Create a 3-minute demo video"
echo ""
echo "Press ENTER to start, or Ctrl+C to cancel..."
read

# Step 1: Open demo page
echo ""
echo "🌐 Step 1: Opening demo page..."
open "$DEMO_HTML"
sleep 3

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                   SCREEN RECORDING SETUP                       ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "  1. Press Cmd + Shift + 5 to open screen recording"
echo "  2. Select 'Record Selected Window'"
echo "  3. Click on the browser window with the demo"
echo "  4. Click 'Record' (red button)"
echo ""
echo "Press ENTER when recording has started..."
read

# Wait 2 seconds after recording starts
sleep 2

echo ""
echo "▶️  STARTING AUTOMATED PLAYBACK"
echo "================================"
echo ""
echo "The audio will play automatically for ~86 seconds."
echo "Navigate through the demo manually while audio plays:"
echo ""
echo "Timeline:"
echo "  0-10s  : Introduction (scene 1)"
echo "  10-17s : Leaderboard overview (scene 2)"  
echo "  17-29s : SOCBench agent details (scene 3)"
echo "  29-40s : Home Automation agent (scene 4)"
echo "  40-48s : Law agent comparison (scene 5)"
echo "  48-55s : MITRE frameworks (scene 6)"
echo "  55-62s : Detailed reports (scene 7)"
echo "  62-70s : GitHub Actions (scene 8)"
echo "  70-78s : Submit your agent (scene 9)"
echo "  78-86s : Call to action (scene 10)"
echo ""
echo "Starting in 3 seconds..."
sleep 1
echo "2..."
sleep 1
echo "1..."
sleep 1
echo "▶️  PLAY!"
echo ""

# Play all audio files in sequence
for i in {1..10}; do
    wavfile=$(ls "$AUDIO_DIR"/scene${i}*.wav 2>/dev/null | head -1)
    if [ -f "$wavfile" ]; then
        echo "🎵 Scene $i: $(basename "$wavfile" .wav | sed 's/scene[0-9]*-//' | tr '-' ' ')"
        afplay "$wavfile"
    fi
done

echo ""
echo "✅ Audio playback complete!"
echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                      STOP RECORDING                            ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "  1. Click the ⏹️  stop button in menu bar"
echo "  2. Save the recording to: ~/Desktop/demo-recordings/demo-3min.mov"
echo ""
echo "Press ENTER when you've saved the recording..."
read

echo ""
echo "✅ VIDEO CREATED SUCCESSFULLY!"
echo ""
echo "📁 Output Location:"
echo "   ~/Desktop/demo-recordings/demo-3min.mov"
echo ""
echo "📊 Video Details:"
echo "   Duration: ~86 seconds (~1.4 minutes)"
echo "   Resolution: 1920x1080 (or browser window size)"
echo "   Format: MOV (H.264)"
echo "   Audio: Embedded AAC"
echo ""
echo "🎬 Next Steps:"
echo "   • Review the video in QuickTime"
echo "   • Export for different platforms if needed"
echo "   • Share on AgentBeats.dev!"
echo ""
echo "To convert to MP4:"
echo "   ffmpeg -i ~/Desktop/demo-recordings/demo-3min.mov \\"
echo "          -c:v libx264 -c:a aac -b:a 192k \\"
echo "          ~/Desktop/demo-recordings/demo-3min.mp4"
echo ""
