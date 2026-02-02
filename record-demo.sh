#!/bin/bash
# 🎬 Automated Demo Recording Script
# This script helps you record the demo video step-by-step

set -e

RECORDING_DIR="$HOME/Desktop/demo-recordings"
TIMESTAMP=$(date +"%Y%m%d-%H%M%S")

# Create recording directory
mkdir -p "$RECORDING_DIR"
cd "$RECORDING_DIR"

echo "🎬 Cyber Security Evaluator - Demo Recording Automation"
echo "========================================================"
echo ""
echo "📁 Recordings will be saved to: $RECORDING_DIR"
echo ""

# Function to wait for user
wait_for_user() {
    echo ""
    echo "⏸️  Press ENTER when ready to continue..."
    read -r
}

# Function to record a take
record_take() {
    local take_name=$1
    local duration=$2
    local description=$3
    
    echo ""
    echo "🎥 TAKE: $take_name"
    echo "⏱️  Duration: $duration seconds"
    echo "📝 Description: $description"
    echo ""
    echo "Instructions:"
    echo "  1. Press ENTER to start recording"
    echo "  2. You'll have 3 seconds to prepare"
    echo "  3. Recording will stop automatically after $duration seconds"
    echo "  4. Press Cmd+Shift+5 and click 'Record Screen' if you prefer manual control"
    echo ""
    
    wait_for_user
    
    echo "🔴 Starting in 3..."
    sleep 1
    echo "🔴 Starting in 2..."
    sleep 1
    echo "🔴 Starting in 1..."
    sleep 1
    echo "🎥 RECORDING NOW! ($duration seconds)"
    echo ""
    
    # Note: macOS screencapture doesn't support timed recording
    # User needs to manually start/stop using Cmd+Shift+5
    echo "⚠️  IMPORTANT: Use macOS built-in screen recorder:"
    echo "   1. Press Cmd+Shift+5"
    echo "   2. Select 'Record Entire Screen' or 'Record Selected Portion'"
    echo "   3. Click Options > Microphone > Built-in Microphone"
    echo "   4. Click 'Record'"
    echo "   5. When done, click Stop button in menu bar"
    echo ""
    echo "⏳ Waiting for you to complete the $duration second recording..."
    sleep "$duration"
    
    echo "✅ $take_name complete!"
    echo ""
}

echo "🎬 DEMO RECORDING WORKFLOW"
echo "=========================="
echo ""
echo "You'll record 6 takes following the DEMO_QUICK_GUIDE.md"
echo ""
echo "Before starting:"
echo "  ✅ Open browser to: https://agentbeats.dev/unicodemonk/cyber-security-evaluator-new"
echo "  ✅ Have 3 tabs ready:"
echo "     - Tab 1: Leaderboard (main page)"
echo "     - Tab 2: SOCBench agent details"
echo "     - Tab 3: GitHub Actions workflows"
echo "  ✅ Close unnecessary apps"
echo "  ✅ Hide desktop icons (optional)"
echo "  ✅ Set browser to full screen"
echo ""

wait_for_user

# Take 1: Title and Leaderboard
record_take "Take 1: Title + Leaderboard" 30 "Show title screen and leaderboard overview"

cat << 'NARRATION1'
📝 NARRATION FOR TAKE 1:
"Welcome to the Cyber Security Evaluator - an automated framework 
for testing AI agent security. This leaderboard shows three agents 
tested against 249 real-world attacks."
NARRATION1

# Take 2: SOCBench Agent (Perfect)
record_take "Take 2: SOCBench Agent" 35 "Show SOCBench agent with 100.0 score"

cat << 'NARRATION2'
📝 NARRATION FOR TAKE 2:
"At the top is the SOCBench code generation agent with a perfect 100 
score. It successfully defended against all 249 attacks including 
system prompt extraction and jailbreak attempts."
NARRATION2

# Take 3: Home Automation Agent (Moderate)
record_take "Take 3: Home Automation" 35 "Show Home Automation agent with 71.69 score"

cat << 'NARRATION3'
📝 NARRATION FOR TAKE 3:
"The home automation agent scored 71.69, showing moderate security. 
It blocked 156 attacks but was vulnerable to 62 system prompt 
extractions and SQL injection attempts."
NARRATION3

# Take 4: Law Purple Agent (Failed)
record_take "Take 4: Law Agent" 35 "Show Law Purple agent with 0.0 score"

cat << 'NARRATION4'
📝 NARRATION FOR TAKE 4:
"The law purple agent scored zero - every single attack succeeded. 
All 219 malicious payloads bypassed its defenses, exposing critical 
system information and allowing complete jailbreak access."
NARRATION4

# Take 5: MITRE Coverage
record_take "Take 5: MITRE Coverage" 30 "Show MITRE ATT&CK and ATLAS techniques"

cat << 'NARRATION5'
📝 NARRATION FOR TAKE 5:
"Each agent is tested against MITRE ATT&CK and ATLAS frameworks. 
We test for prompt injection, jailbreak attempts, system prompt 
extraction, and SQL injection across multiple attack vectors."
NARRATION5

# Take 6: Workflow Demo
record_take "Take 6: GitHub Workflow" 45 "Show GitHub Actions workflow run"

cat << 'NARRATION6'
📝 NARRATION FOR TAKE 6:
"Testing is fully automated through GitHub Actions. Submit your agent, 
and within minutes you'll see comprehensive results including 
vulnerability reports, MITRE technique coverage, and detailed analysis 
of every attack attempt."
NARRATION6

echo ""
echo "🎉 ALL TAKES COMPLETE!"
echo "===================="
echo ""
echo "📁 Your recordings should be in: $HOME/Movies/ or $HOME/Desktop/"
echo ""
echo "Next steps:"
echo "  1. Review your recordings"
echo "  2. Re-record any takes that need improvement"
echo "  3. Use the editing commands in VIDEO_PRODUCTION_COMMANDS.md"
echo "  4. Run the complete workflow script to combine and export"
echo ""
echo "📝 Editing workflow:"
echo "   cd '$RECORDING_DIR'"
echo "   # Rename your recordings to:"
echo "   #   take1-title.mov"
echo "   #   take2-socbench.mov"
echo "   #   take3-homeauto.mov"
echo "   #   take4-law.mov"
echo "   #   take5-mitre.mov"
echo "   #   take6-workflow.mov"
echo ""
echo "   # Then check VIDEO_PRODUCTION_COMMANDS.md for editing commands"
echo ""
echo "🚀 Happy editing!"
