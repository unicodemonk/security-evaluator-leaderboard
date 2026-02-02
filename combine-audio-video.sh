#!/bin/bash
# 🎬 Combine Audio with Video or Create Audio-Visual Demo
# This script helps integrate the generated audio with your demo

set -e

AUDIO_DIR="$HOME/Desktop/demo-recordings/voiceover"
VIDEO_DIR="$HOME/Desktop/demo-recordings"
OUTPUT_DIR="$HOME/Desktop/demo-recordings/final"

mkdir -p "$OUTPUT_DIR"

echo "🎬 Audio-Video Integration Script"
echo "=================================="
echo ""

# Check if we have ffmpeg
if ! command -v ffmpeg &> /dev/null; then
    echo "⚠️  ffmpeg not found. Installing via Homebrew..."
    echo "   Run: brew install ffmpeg"
    echo ""
    echo "   Or continue with manual method below"
    echo ""
    exit 1
fi

echo "✅ ffmpeg found"
echo ""

# First, combine all audio files
echo "🔗 Step 1: Combining all audio files..."
cd "$AUDIO_DIR"

# Create concatenation list
cat > combine-list.txt << 'EOF'
file 'scene1-intro.wav'
file 'scene2-leaderboard.wav'
file 'scene3-socbench.wav'
file 'scene4-homeauto.wav'
file 'scene5-law.wav'
file 'scene6-mitre.wav'
file 'scene7-vulnerabilities.wav'
file 'scene8-github.wav'
file 'scene9-submit.wav'
file 'scene10-cta.wav'
EOF

ffmpeg -f concat -safe 0 -i combine-list.txt -c copy "$OUTPUT_DIR/complete-voiceover.wav" -y

echo "✅ Combined audio created: $OUTPUT_DIR/complete-voiceover.wav"
echo ""

# Check for video recordings
echo "🎥 Step 2: Looking for video recordings..."
VIDEO_FILES=$(find "$VIDEO_DIR" -name "*.mov" -o -name "*.mp4" 2>/dev/null | head -10)

if [ -z "$VIDEO_FILES" ]; then
    echo "⚠️  No video recordings found yet."
    echo ""
    echo "📹 Option A: Record screen now"
    echo "   1. Press Cmd+Shift+5 to start screen recording"
    echo "   2. Navigate through the demo while audio plays"
    echo "   3. Save recording to $VIDEO_DIR"
    echo "   4. Re-run this script"
    echo ""
    echo "📊 Option B: Create slideshow video from HTML demo"
    echo "   We can convert the demo_video/index.html to a video"
    echo ""
    read -p "Create slideshow from HTML demo? (y/n): " choice
    
    if [ "$choice" = "y" ]; then
        echo ""
        echo "🎨 Creating video from HTML demo page..."
        
        # Open the HTML demo
        open "/Users/arch/Documents/SecEval6/security-evaluator-leaderboard/demo_video/index.html"
        
        echo ""
        echo "📹 Instructions:"
        echo "   1. The demo page is now open in your browser"
        echo "   2. Press Cmd+Shift+5"
        echo "   3. Select 'Record Selected Portion' and select the browser window"
        echo "   4. Click through the scenes (they auto-advance)"
        echo "   5. Save as: $VIDEO_DIR/demo-screen-recording.mov"
        echo "   6. Re-run this script to combine with audio"
        echo ""
    fi
    
    exit 0
fi

echo "✅ Found video recordings:"
echo "$VIDEO_FILES"
echo ""

# If we have videos, combine them
echo "🎬 Step 3: Combining videos..."

# Assuming you have multiple takes, combine them
find "$VIDEO_DIR" -name "*.mov" -o -name "*.mp4" | sort | while read video; do
    echo "file '$video'" >> "$OUTPUT_DIR/video-list.txt"
done

if [ -f "$OUTPUT_DIR/video-list.txt" ]; then
    ffmpeg -f concat -safe 0 -i "$OUTPUT_DIR/video-list.txt" -c copy "$OUTPUT_DIR/combined-video-no-audio.mp4" -y
    echo "✅ Combined video created"
    echo ""
fi

# Step 4: Add audio to video
echo "🎵 Step 4: Adding voiceover to video..."

if [ -f "$OUTPUT_DIR/combined-video-no-audio.mp4" ]; then
    ffmpeg -i "$OUTPUT_DIR/combined-video-no-audio.mp4" -i "$OUTPUT_DIR/complete-voiceover.wav" \
        -c:v copy -c:a aac -b:a 192k -shortest \
        "$OUTPUT_DIR/demo-final.mp4" -y
    
    echo "✅ Final video with audio created!"
    echo ""
    echo "📁 $OUTPUT_DIR/demo-final.mp4"
    echo ""
    
    # Open the final video
    open "$OUTPUT_DIR/demo-final.mp4"
fi

echo ""
echo "🎉 Audio-Video Integration Complete!"
echo ""
echo "📂 Output files:"
ls -lh "$OUTPUT_DIR"
echo ""
echo "Next: Export for different platforms using VIDEO_PRODUCTION_COMMANDS.md"
