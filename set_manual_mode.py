import json
import os

SCRIPT_PATH = "/Users/arch/Documents/SecEval6/security-evaluator-leaderboard/demo_video/script.js"

js_content = """
function get(id) {
    return document.getElementById(id);
}

function show(id) {
    document.querySelectorAll('.scene').forEach(el => el.classList.remove('active'));
    const el = get(id);
    if (el) el.classList.add('active');
}

// Global Manual Control
window.manualShow = show;

// Initialize
window.addEventListener('load', () => {
    console.log("Manual Mode Ready");
    // Show nothing or Scene 1 static
    // show('scene-1');
});
"""

with open(SCRIPT_PATH, 'w') as f:
    f.write(js_content)

print("Updated script.js to Manual Mode.")
