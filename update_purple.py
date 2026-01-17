
import os

target_file = "../Cyber-Security-Evaluator/purple_agents/home_automation_agent.py"

new_content = r'''
    @app.post("/")
    @app.post("/command")
    async def handle_command(request_data: dict):
        """
        Handle command request.

        Accepts either:
        1. Direct CommandRequest format
        2. A2A message format with nested command
        """
        try:
            # Try to extract command from A2A message format
            text = None
            if 'parts' in request_data:
                for part in request_data.get('parts', []):
                    if isinstance(part, dict) and 'text' in part:
                        text = part['text']
                        break

            if text:
                # Parse command from text
                command_data = json.loads(text)
            else:
                # Use request data directly
                command_data = request_data

            # Create command request
            req = CommandRequest(**command_data)

            # Process command
            response = agent.process_command(req)
            
            # DEBUGGING: Explicitly dump and log
            resp_dict = response.model_dump(mode='json')
            import json
            resp_json_str = json.dumps(resp_dict)
            logger.info(f"DEBUG RESPONSE FINAL: {resp_json_str}")

            # Return A2A-style response
            return JSONResponse(content={
                "kind": "message",
                "role": "agent",
                "parts": [{
                    "kind": "text",
                    "text": resp_json_str
                }]
            })

        except Exception as e:
            logger.error(f"Error handling command: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return JSONResponse(
                status_code=400,
                content={"error": str(e)}
            )
'''

# Use a smarter replace approach
with open(target_file, "r") as f:
    content = f.read()

# Find the handle_command function and replace it
# We'll look for @app.post("/") and the end of the method
start_marker = '@app.post("/")\n    @app.post("/command")'
end_marker = '@app.get("/state")'

start_idx = content.find(start_marker)
end_idx = content.find(end_marker)

if start_idx != -1 and end_idx != -1:
    content = content[:start_idx] + new_content.strip() + "\n\n    " + content[end_idx:]
    with open(target_file, "w") as f:
        f.write(content)
    print("Successfully replaced handle_command")
else:
    print("Could not find handle_command to replace")
    print(f"Start: {start_idx}, End: {end_idx}")

