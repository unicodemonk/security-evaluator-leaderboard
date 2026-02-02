import subprocess
import os
import json

AUDIO_DIR = "/Users/arch/Documents/SecEval6/SecurityEvaluator"
segments = [
    {
        "id": "01_intro",
        "text": "Welcome to the Cyber Security Evaluator - an automated security assessment platform for AI agents. Today, we'll see how it evaluates three different agents for vulnerabilities using industry-standard MITRE frameworks.",
    },
    {
        "id": "02_leaderboard",
        "text": "Here's our leaderboard with three agents currently evaluated: First, the SOCBench Agent by erenzq - scoring a perfect 100 with zero vulnerabilities detected. Second, our Home Automation Agent - scoring 71 point 6 9 with 62 vulnerabilities found. And third, the Law Purple Agent - scoring zero with 219 critical vulnerabilities.",
    },
    {
        "id": "03_comparison",
        "text": "The comparison shows huge differences. SOCBench is production ready. Home Automation needs work. And Law Purple is critical - do not use.",
    },
    {
        "id": "04_how_it_works",
        "text": "How does it work? Our Green Agent acts as a penetration tester, generating attacks based on MITRE ATT&CK and ATLAS frameworks. It runs 249 tests covering system prompt extraction, jailbreak attacks, and data exfiltration.",
    },
    {
        "id": "05_socbench",
        "text": "Let's examine the top performer - the SOCBench Agent. With a perfect 100 score and zero vulnerabilities, it successfully blocked all malicious attacks while correctly processing all benign requests.",
    },
    {
        "id": "06_homeauto",
        "text": "The Home Automation Agent scores 71 point 6 9. While it blocks most attacks, 62 vulnerabilities were discovered, primarily around IoT command injection and unauthorized access control.",
    },
    {
        "id": "07_law",
        "text": "The Law Purple Agent presents a critical security risk - scoring zero. This agent is completely exposed to system prompt extraction and jailbreaks. All 219 malicious attacks succeeded.",
    },
    {
        "id": "08_mitre",
        "text": "Our evaluator uses industry-standard MITRE frameworks. MITRE ATT&CK covers general security techniques, while MITRE ATLAS focuses specifically on AI and ML security threats.",
    },
    {
        "id": "09_github",
        "text": "The entire evaluation runs automatically on GitHub Actions. The workflow spins up containers, runs all 249 tests, generates detailed reports, and updates the leaderboard - all in under 5 minutes.",
    },
    {
        "id": "10_submit",
        "text": "Want to test your own agent? Create an agent card. Build your Docker image. Submit a configuration via GitHub. Our system automatically evaluates it and adds it to the leaderboard.",
    },
    {
        "id": "11_outro",
        "text": "To recap: We tested three agents with vastly different security postures. The Cyber Security Evaluator provides free, automated security testing. Test your agents today!",
    }
]

timings = []
current_time_ms = 0
BUFFER_MS = 1000  # 1 second buffer between clips

ffmpeg_inputs = ""
ffmpeg_filters = ""
ffmpeg_map = ""

print("Generating audio and calculating timeline...")

for i, seg in enumerate(segments):
    filename = f"audio_{seg['id']}.aiff"
    full_path = os.path.join(AUDIO_DIR, filename)
    
    # Generate audio
    subprocess.call(['say', '-v', 'Samantha', '-o', full_path, seg['text']])
    
    # Get duration
    duration_sec = 0.0
    try:
        out = subprocess.check_output(['afinfo', full_path]).decode('utf-8')
        for line in out.split('\n'):
            if 'duration:' in line:
                duration_sec = float(line.split('duration:')[1].split(' sec')[0].strip())
                break
    except Exception as e:
        print(f"Error getting duration for {filename}: {e}")
        
    duration_ms = int(duration_sec * 1000)
    
    # Store timing
    timings.append({
        "id": seg['id'],
        "file": filename,
        "start_ms": current_time_ms,
        "duration_ms": duration_ms,
        "end_ms": current_time_ms + duration_ms
    })
    
    # Prepare ffmpeg parts
    ffmpeg_inputs += f"-i \"{full_path}\" \\\n"
    ffmpeg_filters += f"[{i+1}]adelay={current_time_ms}|{current_time_ms}[a{i+1}];\n"
    ffmpeg_map += f"[a{i+1}]"

    # Advance time
    current_time_ms += duration_ms + BUFFER_MS

# Save Audio Timings
with open(os.path.join(AUDIO_DIR, 'audio_timings.json'), 'w') as f:
    json.dump({"segments": timings, "total_duration_ms": current_time_ms}, f, indent=2)

# Generate Combine Script
script_content = f"""#!/bin/bash
VIDEO_PATH="/Users/arch/.gemini/antigravity/brain/e40fa02e-d7e1-4d2c-a971-c97c3c1ff5fd/re_record_demo.webp"
OUTPUT_PATH="/Users/arch/Documents/SecEval6/security-evaluator-leaderboard/final_demo_synced.mp4"

echo "Combining synced video and audio..."

/opt/homebrew/bin/ffmpeg -y \\
-i "$VIDEO_PATH" \\
{ffmpeg_inputs}-filter_complex "
{ffmpeg_filters}{ffmpeg_map}amix=inputs={len(segments)}:dropout_transition=0[aout]
" \\
-map 0:v -map "[aout]" \\
-c:v libx264 -pix_fmt yuv420p \\
-c:a aac -b:a 192k \\
"$OUTPUT_PATH"

echo "Done! Saved to $OUTPUT_PATH"
"""

with open(os.path.join(AUDIO_DIR, 'combine_synced.sh'), 'w') as f:
    f.write(script_content)

print(f"Total Duration: {current_time_ms/1000:.2f}s")
print("Generated audio_timings.json and combine_synced.sh")
