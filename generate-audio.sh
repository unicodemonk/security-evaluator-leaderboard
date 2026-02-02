#!/bin/bash
# 🎤 Generate Audio from Voice Over Script
# Uses macOS built-in text-to-speech

set -e

AUDIO_DIR="$HOME/Desktop/demo-recordings/voiceover"
mkdir -p "$AUDIO_DIR"

echo "🎤 Generating Voice Over Audio Files"
echo "===================================="
echo ""
echo "📁 Output directory: $AUDIO_DIR"
echo ""

# List available voices
echo "🗣️  Available voices:"
say -v '?' | head -5
echo ""
echo "Using voice: Samantha (default, natural sounding)"
echo ""

# Scene 1: Introduction (0:00 - 0:30)
echo "🎙️  Generating Scene 1: Introduction..."
say -v Samantha -o "$AUDIO_DIR/scene1-intro.aiff" \
"Welcome to the Cyber Security Evaluator, an automated framework for testing A I agent security. \
This leaderboard shows three agents tested against 249 real-world attacks, including prompt injection, \
jailbreak attempts, and system prompt extraction. Let's see how they performed."

# Scene 2: Leaderboard Overview (0:30 - 0:55)
echo "🎙️  Generating Scene 2: Leaderboard Overview..."
say -v Samantha -o "$AUDIO_DIR/scene2-leaderboard.aiff" \
"The leaderboard ranks agents from A plus to F based on their security posture. \
Each agent is scored on how well it defends against malicious payloads while correctly handling benign requests. \
Zero false positives means no legitimate requests are blocked."

# Scene 3: SOCBench Agent (0:55 - 1:30)
echo "🎙️  Generating Scene 3: SOCBench Agent..."
say -v Samantha -o "$AUDIO_DIR/scene3-socbench.aiff" \
"At the top is the SOC Bench code generation agent with a perfect 100 score. \
It successfully defended against all 249 attacks, including 207 system prompt extraction attempts and 12 jailbreak attacks. \
With zero vulnerabilities and 100 percent accuracy, it earns an A plus grade. \
This agent shows what robust security looks like."

# Scene 4: Home Automation Agent (1:30 - 2:05)
echo "🎙️  Generating Scene 4: Home Automation Agent..."
say -v Samantha -o "$AUDIO_DIR/scene4-homeauto.aiff" \
"The home automation agent scored 71 point 69, showing moderate security. \
It successfully blocked 156 attacks, but was vulnerable to 62 exploits including system prompt extractions \
and S Q L injection attempts. With a C minus grade, this agent needs security improvements before production deployment."

# Scene 5: Law Purple Agent (2:05 - 2:40)
echo "🎙️  Generating Scene 5: Law Purple Agent..."
say -v Samantha -o "$AUDIO_DIR/scene5-law.aiff" \
"The law purple agent scored zero, a critical security failure. \
Every single attack succeeded. All 219 malicious payloads bypassed its defenses, exposing critical system information \
and allowing complete jailbreak access. This agent received an F grade and should not be deployed until major security \
fixes are implemented."

# Scene 6: MITRE ATT&CK (2:40 - 3:10)
echo "🎙️  Generating Scene 6: MITRE Coverage..."
say -v Samantha -o "$AUDIO_DIR/scene6-mitre.aiff" \
"Each agent is tested against the MITRE A T T and C K and ATLAS frameworks, industry-standard security taxonomies. \
We test for prompt injection, jailbreak attempts, system prompt extraction, and S Q L injection across multiple attack vectors. \
This ensures comprehensive security coverage for real-world threats."

# Scene 7: Vulnerability Deep Dive (3:10 - 3:40)
echo "🎙️  Generating Scene 7: Vulnerability Analysis..."
say -v Samantha -o "$AUDIO_DIR/scene7-vulnerabilities.aiff" \
"The vulnerability reports provide detailed analysis of every security issue. \
Each vulnerability includes the MITRE technique I D, C V S S severity score, C W E classification, \
and the exact attack payload that succeeded. This level of detail helps developers understand and fix specific security weaknesses."

# Scene 8: GitHub Actions (3:40 - 4:10)
echo "🎙️  Generating Scene 8: GitHub Integration..."
say -v Samantha -o "$AUDIO_DIR/scene8-github.aiff" \
"Testing is fully automated through GitHub Actions. \
Simply submit your agent configuration, and within minutes you'll see comprehensive results including vulnerability reports, \
MITRE technique coverage, and detailed analysis of every attack attempt. No manual testing required, \
everything runs automatically in the cloud."

# Scene 9: Submit Your Agent (4:10 - 4:40)
echo "🎙️  Generating Scene 9: How to Submit..."
say -v Samantha -o "$AUDIO_DIR/scene9-submit.aiff" \
"Want to test your A I agent? It's free, automated, and takes 5 minutes. \
Submit your agent through the Agent Beats platform, configure your A P I endpoint, and let the framework do the rest. \
You'll get a detailed security report, a leaderboard ranking, and actionable recommendations to improve your agent's security."

# Scene 10: Call to Action (4:40 - 5:00)
echo "🎙️  Generating Scene 10: Call to Action..."
say -v Samantha -o "$AUDIO_DIR/scene10-cta.aiff" \
"Visit Agent Beats dot dev to get started today. \
Test your agent against industry-standard security frameworks and join the growing community of secure A I developers. \
Secure A I for everyone, created by Team Chai G P T: Archana, Jaya, Raj, and Subbu."

echo ""
echo "✅ All audio files generated!"
echo ""

# Convert AIFF to WAV for better compatibility
echo "🔄 Converting to WAV format..."
for file in "$AUDIO_DIR"/*.aiff; do
    basename="${file%.aiff}"
    afconvert -f WAVE -d LEI16 "$file" "${basename}.wav"
done

echo ""
echo "✅ Conversion complete!"
echo ""
echo "📁 Generated files:"
ls -lh "$AUDIO_DIR"/*.wav
echo ""

# Create a combined version
echo "🔗 Creating combined audio file..."
cat > "$AUDIO_DIR/combine.txt" << 'EOF'
# List of all audio files in sequence
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

echo ""
echo "✅ Audio generation complete!"
echo ""
echo "📂 Files saved to: $AUDIO_DIR"
echo ""
echo "📝 Next steps:"
echo "  1. Listen to each scene: open $AUDIO_DIR/scene1-intro.wav"
echo "  2. Adjust timing if needed"
echo "  3. Use VIDEO_PRODUCTION_COMMANDS.md to combine with video"
echo ""
echo "💡 To combine all audio files:"
echo "   cd $AUDIO_DIR"
echo "   # If you have ffmpeg:"
echo "   # ffmpeg -f concat -safe 0 -i combine.txt -c copy final-voiceover.wav"
echo ""
echo "🎬 Ready for video production!"
