
import os

target_file = "../Cyber-Security-Evaluator/purple_agents/home_automation_agent.py"

with open(target_file, "r") as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    new_lines.append(line)
    if "response = agent.process_command(req)" in line:
        indent = line[:line.find("response")]
        new_lines.append(f'{indent}logger.info(f"DEBUG RESPONSE: {{response.model_dump_json()}}")\n')

with open(target_file, "w") as f:
    f.writelines(new_lines)

print("File modified.")
