import subprocess
import os
import json

segments = [
    {
        "id": "01_intro",
        "text": "Welcome to the Cyber Security Evaluator - an automated security assessment platform for AI agents. Today, we'll see how it evaluates three different agents for vulnerabilities using industry-standard MITRE frameworks.",
        "start_time": 0
    },
    {
        "id": "02_leaderboard",
        "text": "Here's our leaderboard with three agents currently evaluated: First, the SOCBench Agent by erenzq - scoring a perfect 100 with zero vulnerabilities detected. Second, our Home Automation Agent - scoring 71 point 6 9 with 62 vulnerabilities found. And third, the Law Purple Agent - scoring zero with 219 critical vulnerabilities.",
        "start_time": 12 
    },
    {
        "id": "03_comparison",
        "text": "The comparison shows huge differences. SOCBench is production ready. Home Automation needs work. And Law Purple is critical - do not use.",
        "start_time": 30
    },
    {
        "id": "04_how_it_works",
        "text": "How does it work? Our Green Agent acts as a penetration tester, generating attacks based on MITRE ATT&CK and ATLAS frameworks. It runs 249 tests covering system prompt extraction, jailbreak attacks, and data exfiltration.",
        "start_time": 45
    },
    {
        "id": "05_socbench",
        "text": "Let's examine the top performer - the SOCBench Agent. With a perfect 100 score and zero vulnerabilities, it successfully blocked all malicious attacks while correctly processing all benign requests.",
        "start_time": 60
    },
    {
        "id": "06_homeauto",
        "text": "The Home Automation Agent scores 71 point 6 9. While it blocks most attacks, 62 vulnerabilities were discovered, primarily around IoT command injection and unauthorized access control.",
        "start_time": 90
    },
    {
        "id": "07_law",
        "text": "The Law Purple Agent presents a critical security risk - scoring zero. This agent is completely exposed to system prompt extraction and jailbreaks. All 219 malicious attacks succeeded.",
        "start_time": 120
    },
    {
        "id": "08_mitre",
        "text": "Our evaluator uses industry-standard MITRE frameworks. MITRE ATT&CK covers general security techniques, while MITRE ATLAS focuses specifically on AI and ML security threats.",
        "start_time": 165
    },
    {
        "id": "09_github",
        "text": "The entire evaluation runs automatically on GitHub Actions. The workflow spins up containers, runs all 249 tests, generates detailed reports, and updates the leaderboard - all in under 5 minutes.",
        "start_time": 180
    },
    {
        "id": "10_submit",
        "text": "Want to test your own agent? Create an agent card. Build your Docker image. Submit a configuration via GitHub. Our system automatically evaluates it and adds it to the leaderboard.",
        "start_time": 210
    },
    {
        "id": "11_outro",
        "text": "To recap: We tested three agents with vastly different security postures. The Cyber Security Evaluator provides free, automated security testing. Test your agents today!",
        "start_time": 250
    }
]

durations = {}

for seg in segments:
    filename = f"audio_{seg['id']}.aiff"
    print(f"Generating {filename}...")
    subprocess.call(['say', '-v', 'Samantha', '-o', filename, seg['text']])
    
    # Get duration using afinfo (macOS built-in)
    # output: "duration: 12.345 sec"
    try:
        out = subprocess.check_output(['afinfo', filename]).decode('utf-8')
        for line in out.split('\n'):
            if 'duration:' in line:
                dur = float(line.split('duration:')[1].split(' sec')[0].strip())
                durations[seg['id']] = dur
                print(f"Duration: {dur:.2f}s")
                break
    except Exception as e:
        print(f"Error getting duration for {filename}: {e}")

# Save durations to json for next step
with open('audio_durations.json', 'w') as f:
    json.dump(durations, f, indent=2)

print("Done generating audio.")
