#!/bin/bash
# 🎤 Generate 3-Minute Voice Over Audio
# Condensed version for 3-minute demo video

set -e

AUDIO_DIR="$HOME/Desktop/demo-recordings/voiceover-3min"
mkdir -p "$AUDIO_DIR"

echo "🎤 Generating 3-Minute Voice Over Audio"
echo "========================================"
echo ""
echo "📁 Output directory: $AUDIO_DIR"
echo "⏱️  Target length: 3 minutes (180 seconds)"
echo ""
echo "Using voice: Samantha"
echo ""

# Scene 1: Introduction (15s)
echo "🎙️  Scene 1: Introduction (15s)..."
say -v Samantha -o "$AUDIO_DIR/scene1-intro.aiff" \
"Welcome to the Cyber Security Evaluator. Automated testing for A I agent security. \
Three agents, 249 attacks. Let's see the results."

# Scene 2: Leaderboard (15s)
echo "🎙️  Scene 2: Leaderboard (15s)..."
say -v Samantha -o "$AUDIO_DIR/scene2-leaderboard.aiff" \
"The leaderboard ranks agents from A plus to F. Each is scored on defense against malicious payloads \
while handling legitimate requests."

# Scene 3: SOCBench Perfect (20s)
echo "🎙️  Scene 3: SOCBench Perfect (20s)..."
say -v Samantha -o "$AUDIO_DIR/scene3-socbench.aiff" \
"SOC Bench code generation agent: perfect 100 score. Defended against all 249 attacks. \
Zero vulnerabilities. A plus grade. This is what robust security looks like."

# Scene 4: Home Automation Moderate (20s)
echo "🎙️  Scene 4: Home Automation (20s)..."
say -v Samantha -o "$AUDIO_DIR/scene4-homeauto.aiff" \
"Home automation agent: 71 point 69. Blocked 156 attacks but vulnerable to 62 exploits. \
C minus grade. Needs security improvements."

# Scene 5: Law Agent Failed (20s)
echo "🎙️  Scene 5: Law Agent Failed (20s)..."
say -v Samantha -o "$AUDIO_DIR/scene5-law.aiff" \
"Law purple agent: zero score. Every attack succeeded. 219 vulnerabilities found. \
F grade. Do not deploy."

# Scene 6: MITRE Testing (15s)
echo "🎙️  Scene 6: MITRE Testing (15s)..."
say -v Samantha -o "$AUDIO_DIR/scene6-mitre.aiff" \
"Each agent tested against MITRE A T T and C K and ATLAS frameworks. \
Industry-standard security taxonomies."

# Scene 7: Detailed Reports (15s)
echo "🎙️  Scene 7: Reports (15s)..."
say -v Samantha -o "$AUDIO_DIR/scene7-reports.aiff" \
"Detailed vulnerability reports include MITRE technique I D, C V S S scores, \
and exact attack payloads."

# Scene 8: GitHub Automation (20s)
echo "🎙️  Scene 8: GitHub Automation (20s)..."
say -v Samantha -o "$AUDIO_DIR/scene8-github.aiff" \
"Fully automated through GitHub Actions. Submit your agent, get comprehensive results in minutes. \
No manual testing required."

# Scene 9: How to Submit (20s)
echo "🎙️  Scene 9: Submit Agent (20s)..."
say -v Samantha -o "$AUDIO_DIR/scene9-submit.aiff" \
"Want to test your A I agent? Free, automated, takes 5 minutes. \
Get detailed security reports and leaderboard ranking."

# Scene 10: Call to Action (20s)
echo "🎙️  Scene 10: Call to Action (20s)..."
say -v Samantha -o "$AUDIO_DIR/scene10-cta.aiff" \
"Visit Agent Beats dot dev to get started. Test against industry-standard frameworks. \
Secure A I for everyone. By Team Chai G P T."

echo ""
echo "✅ All audio generated!"
echo ""

# Convert to WAV
echo "🔄 Converting to WAV..."
for file in "$AUDIO_DIR"/*.aiff; do
    basename="${file%.aiff}"
    afconvert -f WAVE -d LEI16 "$file" "${basename}.wav"
    rm "$file"
done

echo ""
echo "✅ Conversion complete!"
echo ""
echo "📁 Generated files:"
ls -lh "$AUDIO_DIR"/*.wav

# Get durations
echo ""
echo "⏱️  Scene durations:"
for file in "$AUDIO_DIR"/*.wav; do
    duration=$(afinfo "$file" 2>/dev/null | grep "estimated duration" | awk '{print $3}')
    echo "  $(basename "$file"): ${duration}s"
done

echo ""
echo "✅ 3-minute audio complete!"
echo "📂 Location: $AUDIO_DIR"
