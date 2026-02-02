#!/bin/bash
# 🎬 Create 3-Minute Demo Video from HTML + Audio
# Automated video creation without manual recording

set -e

AUDIO_DIR="$HOME/Desktop/demo-recordings/voiceover-3min"
OUTPUT_DIR="$HOME/Desktop/demo-recordings/final"
HTML_FILE="/Users/arch/Documents/SecEval6/security-evaluator-leaderboard/demo_video/index.html"

mkdir -p "$OUTPUT_DIR"

echo "🎬 Creating 3-Minute Demo Video"
echo "================================"
echo ""

# Check for required tools
if ! command -v ffmpeg &> /dev/null; then
    echo "📦 Installing ffmpeg..."
    brew install ffmpeg
fi

echo "✅ Tools ready"
echo ""

# Step 1: Combine all audio files
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

ffmpeg -f concat -safe 0 -i combine-list.txt -c copy "$OUTPUT_DIR/complete-voiceover-3min.wav" -y 2>/dev/null

# Get total duration
AUDIO_DURATION=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$OUTPUT_DIR/complete-voiceover-3min.wav")
echo "✅ Combined audio: ${AUDIO_DURATION}s"
echo ""

# Step 2: Create video from images/screenshots
echo "🎨 Step 2: Creating video frames..."

# We'll create a simple slideshow using solid colors and text overlays
# Each frame represents a scene from the demo

# Create frames directory
FRAMES_DIR="$OUTPUT_DIR/frames"
mkdir -p "$FRAMES_DIR"

echo "  Creating title card..."
ffmpeg -f lavfi -i color=c=#0f172a:s=1920x1080:d=0.1 -vf \
"drawtext=text='CYBER SECURITY EVALUATOR':fontsize=72:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2-100,\
drawtext=text='Automated AI Agent Security Testing':fontsize=36:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2+50,\
drawtext=text='by Team ChAI GPT (Archana, Jaya, Raj & Subbu)':fontsize=24:fontcolor=#64748b:x=(w-text_w)/2:y=(h-text_h)/2+150" \
"$FRAMES_DIR/frame1.png" -y 2>/dev/null

echo "  Creating leaderboard frame..."
ffmpeg -f lavfi -i color=c=#0f172a:s=1920x1080:d=0.1 -vf \
"drawtext=text='LEADERBOARD':fontsize=64:fontcolor=white:x=(w-text_w)/2:y=100,\
drawtext=text='Purple Agent Security Rankings':fontsize=32:fontcolor=#94a3b8:x=(w-text_w)/2:y=200
"$FRAMES_DIR/frame2.png" -y 2>/dev/null

echo "  Creating SOCBench frame..."
ffmpeg -f lavfi -i color=c=#0f172a:s=1920x1080:d=0.1 -vf \
"drawtext=text='SOCBench Agent':fontsize=56:fontcolor=white:x=(w-text_w)/2:y=200,\
drawtext=text='100.0':fontsize=120:fontcolor=#22c55e:x=(w-text_w)/2:y=350,\
drawtext=text='A+ Grade | 0 Vulnerabilities':fontsize=40:fontcolor=#22c55e:x=(w-text_w)/2:y=550,\
drawtext=text='Perfect Security':fontsize=32:fontcolor=#94a3b8:x=(w-text_w)/2:y=700
"$FRAMES_DIR/frame3.png" -y 2>/dev/null

echo "  Creating Home Automation frame..."
ffmpeg -f lavfi -i color=c=#0f172a:s=1920x1080:d=0.1 -vf \
"drawtext=text='Home Automation Agent':fontsize=56:fontcolor=white:x=(w-text_w)/2:y=200,\
drawtext=text='71.69':fontsize=120:fontcolor=#eab308:x=(w-text_w)/2:y=350,\
drawtext=text='C- Grade | 62 Vulnerabilities':fontsize=40:fontcolor=#eab308:x=(w-text_w)/2:y=550,\
drawtext=text='Moderate Security':fontsize=32:fontcolor=#94a3b8:x=(w-text_w)/2:y=700
"$FRAMES_DIR/frame4.png" -y 2>/dev/null

echo "  Creating Law Agent frame..."
ffmpeg -f lavfi -i color=c=#0f172a:s=1920x1080:d=0.1 -vf \
"drawtext=text='Law Purple Agent':fontsize=56:fontcolor=white:x=(w-text_w)/2:y=200,\
drawtext=text='0.0':fontsize=120:fontcolor=#ef4444:x=(w-text_w)/2:y=350,\
drawtext=text='F Grade | 219 Vulnerabilities':fontsize=40:fontcolor=#ef4444:x=(w-text_w)/2:y=550,\
drawtext=text='CRITICAL FAILURE':fontsize=32:fontcolor=#ef4444:x=(w-text_w)/2:y=700
"$FRAMES_DIR/frame5.png" -y 2>/dev/null

echo "  Creating MITRE frame..."
ffmpeg -f lavfi -i color=c=#0f172a:s=1920x1080:d=0.1 -vf \
"drawtext=text='MITRE ATT&CK + ATLAS':fontsize=64:fontcolor=white:x=(w-text_w)/2:y=300,\
drawtext=text='Industry-Standard Security Frameworks':fontsize=36:fontcolor=#94a3b8:x=(w-text_w)/2:y=450,\
drawtext=text='249 Real-World Attack Tests':fontsize=32:fontcolor=#64748b:x=(w-text_w)/2:y=600
"$FRAMES_DIR/frame6.png" -y 2>/dev/null

echo "  Creating Reports frame..."
ffmpeg -f lavfi -i color=c=#0f172a:s=1920x1080:d=0.1 -vf \
"drawtext=text='DETAILED REPORTS':fontsize=64:fontcolor=white:x=(w-text_w)/2:y=300,\
drawtext=text='• MITRE Technique IDs':fontsize=36:fontcolor=#94a3b8:x=400:y=450,\
drawtext=text='• CVSS Severity Scores':fontsize=36:fontcolor=#94a3b8:x=400:y=520,\
drawtext=text='• Attack Payloads':fontsize=36:fontcolor=#94a3b8:x=400:y=590
"$FRAMES_DIR/frame7.png" -y 2>/dev/null

echo "  Creating GitHub frame..."
ffmpeg -f lavfi -i color=c=#0f172a:s=1920x1080:d=0.1 -vf \
"drawtext=text='GITHUB ACTIONS':fontsize=64:fontcolor=white:x=(w-text_w)/2:y=250,\
drawtext=text='Fully Automated Testing':fontsize=40:fontcolor=#94a3b8:x=(w-text_w)/2:y=400,\
drawtext=text='Results in Minutes':fontsize=40:fontcolor=#94a3b8:x=(w-text_w)/2:y=500,\
drawtext=text='No Manual Work Required':fontsize=40:fontcolor=#94a3b8:x=(w-text_w)/2:y=600
"$FRAMES_DIR/frame8.png" -y 2>/dev/null

echo "  Creating Submit frame..."
ffmpeg -f lavfi -i color=c=#0f172a:s=1920x1080:d=0.1 -vf \
"drawtext=text='TEST YOUR AGENT':fontsize=64:fontcolor=white:x=(w-text_w)/2:y=250,\
drawtext=text='✓ Free':fontsize=44:fontcolor=#22c55e:x=(w-text_w)/2:y=400,\
drawtext=text='✓ Automated':fontsize=44:fontcolor=#22c55e:x=(w-text_w)/2:y=480,\
drawtext=text='✓ 5 Minutes':fontsize=44:fontcolor=#22c55e:x=(w-text_w)/2:y=560
"$FRAMES_DIR/frame9.png" -y 2>/dev/null

echo "  Creating CTA frame..."
ffmpeg -f lavfi -i color=c=#0f172a:s=1920x1080:d=0.1 -vf \
"drawtext=text='AgentBeats.dev':fontsize=72:fontcolor=#3b82f6:x=(w-text_w)/2:y=300,\
drawtext=text='Secure AI for Everyone':fontsize=40:fontcolor=#94a3b8:x=(w-text_w)/2:y=500,\
drawtext=text='by Team ChAI GPT':fontsize=28:fontcolor=#64748b:x=(w-text_w)/2:y=650
"$FRAMES_DIR/frame10.png" -y 2>/dev/null

echo "✅ Frames created"
echo ""

# Step 3: Create video from frames with proper timing
echo "🎬 Step 3: Creating video with timed frames..."

# Calculate durations for each scene (approximate)
cat > "$FRAMES_DIR/frame-durations.txt" << 'EOF'
file 'frame1.png'
duration 15
file 'frame2.png'
duration 15
file 'frame3.png'
duration 20
file 'frame4.png'
duration 20
file 'frame5.png'
duration 20
file 'frame6.png'
duration 15
file 'frame7.png'
duration 15
file 'frame8.png'
duration 20
file 'frame9.png'
duration 20
file 'frame10.png'
duration 20
file 'frame10.png'
EOF

cd "$FRAMES_DIR"
ffmpeg -f concat -safe 0 -i frame-durations.txt -vf "fps=30,format=yuv420p" -c:v libx264 -preset fast "$OUTPUT_DIR/video-silent.mp4" -y 2>/dev/null

echo "✅ Video frames assembled"
echo ""

# Step 4: Combine video with audio
echo "🎵 Step 4: Adding audio to video..."

ffmpeg -i "$OUTPUT_DIR/video-silent.mp4" -i "$OUTPUT_DIR/complete-voiceover-3min.wav" \
    -c:v copy -c:a aac -b:a 192k -shortest \
    "$OUTPUT_DIR/demo-3min-FINAL.mp4" -y 2>/dev/null

echo "✅ Video with audio created!"
echo ""

# Step 5: Verify duration
FINAL_DURATION=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$OUTPUT_DIR/demo-3min-FINAL.mp4")
MINUTES=$(echo "$FINAL_DURATION / 60" | bc)
SECONDS=$(echo "$FINAL_DURATION % 60" | bc)

echo "🎉 DEMO VIDEO COMPLETE!"
echo "======================="
echo ""
echo "📁 File: $OUTPUT_DIR/demo-3min-FINAL.mp4"
echo "⏱️  Duration: ${MINUTES}m ${SECONDS}s"
echo "📊 Resolution: 1920x1080 @ 30fps"
echo "🎵 Audio: AAC 192kbps"
echo ""

# Open the final video
open "$OUTPUT_DIR/demo-3min-FINAL.mp4"

echo "✅ Video opened in player!"
echo ""
echo "📤 Export for platforms:"
echo "   YouTube: Already optimized!"
echo "   Twitter: Run VIDEO_PRODUCTION_COMMANDS.md for 720p version"
echo "   Instagram: Run VIDEO_PRODUCTION_COMMANDS.md for 1:1 version"
