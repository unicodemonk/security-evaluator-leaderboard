# 🎬 Demo Video Production Commands

Quick commands and scripts to help create the demo video.

---

## 📹 Screen Recording

### macOS (QuickTime)
```bash
# Start screen recording with audio
# File > New Screen Recording
# Click Options > Show Mouse Clicks in Recording
# Click red button to start

# Or use command line (no audio):
screencapture -v ~/Desktop/demo-recording.mov
```

### macOS (Screenshot.app with audio)
```bash
# Press: Cmd + Shift + 5
# Select: Record Entire Screen or Record Selected Portion
# Options > Microphone > Built-in Microphone
# Click Record
```

### Using ffmpeg (Advanced)
```bash
# Record screen on macOS
ffmpeg -f avfoundation -i "1:0" -r 30 -s 1920x1080 \
  -c:v libx264 -preset ultrafast -crf 18 \
  ~/Desktop/demo-recording.mp4

# Record with audio
ffmpeg -f avfoundation -i "1:0" -i "0" -r 30 \
  -c:v libx264 -preset ultrafast -crf 18 \
  -c:a aac -b:a 192k \
  ~/Desktop/demo-with-audio.mp4
```

---

## 🎤 Audio Recording

### Record voiceover separately
```bash
# Using QuickTime
# File > New Audio Recording
# Click red button, read script

# Using sox (command line)
sox -d -r 48000 -c 2 ~/Desktop/voiceover.wav

# Convert to mp3
ffmpeg -i ~/Desktop/voiceover.wav -b:a 192k ~/Desktop/voiceover.mp3
```

### Clean up audio
```bash
# Remove background noise with ffmpeg
ffmpeg -i voiceover.wav -af "highpass=f=200, lowpass=f=3000" voiceover-clean.wav

# Normalize volume
ffmpeg -i voiceover-clean.wav -filter:a loudnorm voiceover-normalized.wav
```

---

## ✂️ Video Editing Commands

### Cut video segments
```bash
# Extract segment (start at 10s, duration 30s)
ffmpeg -i demo-recording.mp4 -ss 00:00:10 -t 00:00:30 -c copy segment1.mp4

# Cut multiple segments
ffmpeg -i demo.mp4 -ss 00:00:00 -to 00:00:30 -c copy intro.mp4
ffmpeg -i demo.mp4 -ss 00:00:30 -to 00:01:00 -c copy part1.mp4
ffmpeg -i demo.mp4 -ss 00:01:00 -to 00:01:30 -c copy part2.mp4
```

### Concatenate clips
```bash
# Create file list
cat > segments.txt << EOF
file 'intro.mp4'
file 'part1.mp4'
file 'part2.mp4'
file 'outro.mp4'
EOF

# Concatenate
ffmpeg -f concat -safe 0 -i segments.txt -c copy final-video.mp4
```

### Speed up/slow down
```bash
# Speed up 1.5x (for boring parts)
ffmpeg -i input.mp4 -filter:v "setpts=0.67*PTS" -an output-fast.mp4

# Slow down 0.5x (for emphasis)
ffmpeg -i input.mp4 -filter:v "setpts=2.0*PTS" output-slow.mp4
```

### Add zoom effect
```bash
# Zoom to 120% (focus on detail)
ffmpeg -i input.mp4 -vf "scale=iw*1.2:ih*1.2,crop=1920:1080" output-zoomed.mp4

# Smooth zoom in (0.5s)
ffmpeg -i input.mp4 -vf "zoompan=z='min(zoom+0.0015,1.5)':d=125:s=1920x1080" output-zoom-in.mp4
```

---

## 🎨 Add Graphics Overlay

### Add text overlay
```bash
# Simple text at top
ffmpeg -i input.mp4 -vf "drawtext=text='Cyber Security Evaluator':fontfile=/System/Library/Fonts/Helvetica.ttc:fontsize=48:fontcolor=white:x=(w-text_w)/2:y=50" output-with-title.mp4

# Text with background box
ffmpeg -i input.mp4 -vf "drawtext=text='100.0 Score':fontsize=36:fontcolor=white:box=1:boxcolor=black@0.5:boxborderw=5:x=(w-text_w)/2:y=100" output-with-box.mp4

# Animated text (fade in)
ffmpeg -i input.mp4 -vf "drawtext=text='Perfect Security':fontsize=48:fontcolor=white:alpha='if(lt(t,1),0,if(lt(t,2),(t-1)/1,1))':x=(w-text_w)/2:y=(h-text_h)/2" output-fade-in.mp4
```

### Add watermark
```bash
# Add logo in corner
ffmpeg -i input.mp4 -i logo.png -filter_complex "overlay=10:10" output-with-logo.mp4

# Add text watermark
ffmpeg -i input.mp4 -vf "drawtext=text='@unicodemonk':fontsize=24:fontcolor=white@0.5:x=w-tw-10:y=h-th-10" output-watermarked.mp4
```

---

## 🎵 Audio Mixing

### Add background music
```bash
# Mix voiceover with background music (music at 20% volume)
ffmpeg -i video.mp4 -i voiceover.mp3 -i background-music.mp3 \
  -filter_complex "[2:a]volume=0.2[bg];[1:a][bg]amix=inputs=2:duration=first[audio]" \
  -map 0:v -map "[audio]" -c:v copy -c:a aac -b:a 192k \
  output-with-audio.mp4
```

### Audio fade in/out
```bash
# Fade in (3s) and fade out (3s)
ffmpeg -i audio.mp3 -af "afade=t=in:st=0:d=3,afade=t=out:st=27:d=3" audio-faded.mp3
```

### Sync audio to video
```bash
# Replace video audio with voiceover
ffmpeg -i video.mp4 -i voiceover.mp3 -c:v copy -map 0:v:0 -map 1:a:0 -shortest output.mp4
```

---

## 🎞️ Create Title Cards

### Generate title image
```bash
# Create black background with white text
ffmpeg -f lavfi -i color=c=black:s=1920x1080:d=5 \
  -vf "drawtext=text='Cyber Security Evaluator':fontfile=/System/Library/Fonts/Helvetica.ttc:fontsize=72:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2" \
  title-card.mp4
```

### Create gradient background
```bash
# Blue to black gradient
ffmpeg -f lavfi -i "gradients=s=1920x1080:c0=0x1e3a8a:c1=0x000000:n=2:d=5" \
  gradient-bg.mp4
```

---

## 📊 Export for Different Platforms

### YouTube (1080p, H.264)
```bash
ffmpeg -i final-video.mp4 \
  -c:v libx264 -preset slow -crf 18 \
  -c:a aac -b:a 192k -ar 48000 \
  -vf "scale=1920:1080,fps=30" \
  -movflags +faststart \
  youtube-1080p.mp4
```

### Twitter (720p, max 2:20)
```bash
# Trim to 2:20 and scale to 720p
ffmpeg -i final-video.mp4 -t 140 \
  -c:v libx264 -preset fast -crf 22 \
  -c:a aac -b:a 128k \
  -vf "scale=1280:720,fps=30" \
  -movflags +faststart \
  twitter.mp4
```

### Instagram (Square 1:1)
```bash
# Crop to square and scale to 1080x1080
ffmpeg -i final-video.mp4 \
  -vf "crop=ih:ih,scale=1080:1080,fps=30" \
  -c:v libx264 -preset fast -crf 22 \
  -c:a aac -b:a 128k -ar 48000 \
  -t 60 \
  instagram.mp4
```

### TikTok (Vertical 9:16)
```bash
# Crop to 9:16 vertical
ffmpeg -i final-video.mp4 \
  -vf "crop=ih*9/16:ih,scale=1080:1920,fps=30" \
  -c:v libx264 -preset fast -crf 22 \
  -c:a aac -b:a 128k \
  -t 60 \
  tiktok.mp4
```

### LinkedIn (Professional)
```bash
ffmpeg -i final-video.mp4 \
  -c:v libx264 -preset medium -crf 20 \
  -c:a aac -b:a 192k \
  -vf "scale=1920:1080,fps=30" \
  -t 180 \
  linkedin.mp4
```

---

## 🎬 Complete Workflow Example

```bash
#!/bin/bash
# Complete video production workflow

echo "🎬 Starting video production..."

# 1. Clean up audio
echo "📝 Processing voiceover..."
ffmpeg -i raw-voiceover.wav \
  -af "highpass=f=200,lowpass=f=3000,loudnorm" \
  -y voiceover-clean.wav

# 2. Extract key segments from screen recording
echo "✂️ Extracting segments..."
ffmpeg -i screen-recording.mp4 -ss 00:00:05 -t 00:00:25 -c copy segment-intro.mp4
ffmpeg -i screen-recording.mp4 -ss 00:00:30 -t 00:00:30 -c copy segment-agent1.mp4
ffmpeg -i screen-recording.mp4 -ss 00:01:00 -t 00:00:30 -c copy segment-agent2.mp4
ffmpeg -i screen-recording.mp4 -ss 00:01:30 -t 00:00:45 -c copy segment-agent3.mp4

# 3. Create title card
echo "🎨 Creating title card..."
ffmpeg -f lavfi -i color=c=#1e3a8a:s=1920x1080:d=5 \
  -vf "drawtext=text='Cyber Security Evaluator':fontfile=/System/Library/Fonts/Helvetica.ttc:fontsize=72:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2-100,drawtext=text='Automated AI Agent Security Testing':fontsize=36:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2+100" \
  -y title.mp4

# 4. Concatenate all segments
echo "🔗 Concatenating segments..."
cat > segments.txt << EOF
file 'title.mp4'
file 'segment-intro.mp4'
file 'segment-agent1.mp4'
file 'segment-agent2.mp4'
file 'segment-agent3.mp4'
EOF

ffmpeg -f concat -safe 0 -i segments.txt -c copy video-no-audio.mp4

# 5. Add voiceover and background music
echo "🎵 Adding audio..."
ffmpeg -i video-no-audio.mp4 -i voiceover-clean.wav -i background-music.mp3 \
  -filter_complex "[2:a]volume=0.15[bg];[1:a][bg]amix=inputs=2:duration=first:dropout_transition=3[audio]" \
  -map 0:v -map "[audio]" \
  -c:v copy -c:a aac -b:a 192k \
  -y final-video-draft.mp4

# 6. Add text overlays for key metrics
echo "📊 Adding overlays..."
ffmpeg -i final-video-draft.mp4 \
  -vf "drawtext=text='SOCBench: 100.0 (A+)':enable='between(t,30,35)':fontsize=48:fontcolor=white:box=1:boxcolor=green@0.7:boxborderw=5:x=(w-text_w)/2:y=100" \
  -c:a copy \
  -y final-video.mp4

# 7. Export for different platforms
echo "📱 Exporting for platforms..."

# YouTube
ffmpeg -i final-video.mp4 \
  -c:v libx264 -preset slow -crf 18 \
  -c:a aac -b:a 192k \
  -vf "scale=1920:1080,fps=30" \
  -movflags +faststart \
  -y youtube.mp4

# Twitter (trim to 2:20)
ffmpeg -i final-video.mp4 -t 140 \
  -c:v libx264 -preset fast -crf 22 \
  -c:a aac -b:a 128k \
  -vf "scale=1280:720,fps=30" \
  -movflags +faststart \
  -y twitter.mp4

# Instagram Square
ffmpeg -i final-video.mp4 \
  -vf "crop=ih:ih,scale=1080:1080,fps=30" \
  -c:v libx264 -preset fast -crf 22 \
  -c:a aac -b:a 128k \
  -t 60 \
  -y instagram.mp4

echo "✅ Done! Files created:"
ls -lh youtube.mp4 twitter.mp4 instagram.mp4 final-video.mp4

# Clean up temp files
rm segments.txt segment-*.mp4 title.mp4 video-no-audio.mp4 final-video-draft.mp4

echo "🎉 Video production complete!"
```

---

## 🎯 Quick One-Liners

### Add subtitles/captions
```bash
# Generate subtitle file with auto-captions (requires whisper)
whisper screen-recording.mp4 --model base --output_format srt

# Burn subtitles into video
ffmpeg -i video.mp4 -vf subtitles=captions.srt output-with-subs.mp4
```

### Create thumbnail
```bash
# Extract frame at 30 seconds
ffmpeg -i final-video.mp4 -ss 00:00:30 -vframes 1 thumbnail.jpg

# Create custom thumbnail with text
ffmpeg -f lavfi -i color=c=#1e3a8a:s=1920x1080 -frames:v 1 \
  -vf "drawtext=text='3 Agents Tested':fontsize=96:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2-100,drawtext=text='Results Will Shock You':fontsize=64:fontcolor=#fbbf24:x=(w-text_w)/2:y=(h-text_h)/2+100" \
  custom-thumbnail.jpg
```

### Generate preview GIF
```bash
# Create 5-second GIF preview (for social media)
ffmpeg -i final-video.mp4 -t 5 -vf "fps=10,scale=640:-1:flags=lanczos" -loop 0 preview.gif
```

### Get video info
```bash
# Show detailed video information
ffprobe -v quiet -print_format json -show_format -show_streams final-video.mp4

# Quick stats
ffmpeg -i final-video.mp4 2>&1 | grep Duration
```

---

## 🔧 Troubleshooting

### Video has no audio
```bash
# Check if video has audio stream
ffprobe -v error -show_entries stream=codec_type -of default=nw=1 video.mp4

# Add silent audio if missing
ffmpeg -i video.mp4 -f lavfi -i anullsrc=r=48000:cl=stereo -c:v copy -c:a aac -shortest output.mp4
```

### Audio out of sync
```bash
# Delay audio by 0.5 seconds
ffmpeg -i video.mp4 -itsoffset 0.5 -i audio.mp3 -map 0:v -map 1:a -c copy output.mp4

# Speed up audio by 2%
ffmpeg -i audio.mp3 -filter:a "atempo=1.02" audio-adjusted.mp3
```

### File size too large
```bash
# Reduce file size (increase CRF = more compression)
ffmpeg -i large-video.mp4 -c:v libx264 -crf 28 -c:a aac -b:a 128k smaller-video.mp4

# Two-pass encoding for better quality at target size
ffmpeg -i input.mp4 -c:v libx264 -b:v 2M -pass 1 -f mp4 /dev/null
ffmpeg -i input.mp4 -c:v libx264 -b:v 2M -pass 2 output.mp4
```

---

## 📦 Install Required Tools

```bash
# macOS (using Homebrew)
brew install ffmpeg
brew install sox
brew install whisper  # for auto-captions

# Verify installation
ffmpeg -version
sox --version
```

---

## 🎬 Ready to Create!

Save this file and run the commands as needed. For the complete workflow, save the script section as `produce-video.sh` and run:

```bash
chmod +x produce-video.sh
./produce-video.sh
```

Good luck with your demo video! 🚀
