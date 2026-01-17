
import os

target_file = "../Cyber-Security-Evaluator/purple_agents/home_automation_agent.py"

new_content = r'''
    import threading
    _agent_lock = threading.Lock()

    @app.post("/")
    @app.post("/command")
    def handle_command(request_data: dict):
        """
        Handle command request.
        Sync version with lock to prevent race conditions on agent state.
        Accepts either:
        1. Direct CommandRequest format
        2. A2A message format with nested command
        """
        import json
        import traceback

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

            # Process command with thread lock
            # global _agent_lock - REMOVED to allow closure access
            with _agent_lock:
                response = agent.process_command(req)
            
            # DEBUGGING: Explicitly dump and log
            if hasattr(response, 'model_dump'):
                resp_dict = response.model_dump(mode='json')
            else:
                resp_dict = response.dict()
            
            # Force add missing fields if they are somehow missing
            resp_dict['test_case_id'] = getattr(response, 'test_case_id', 'unknown')
            resp_dict['is_vulnerable'] = getattr(response, 'is_vulnerable', False)

            resp_json_str = json.dumps(resp_dict)
            logger.info(f"DEBUG RESPONSE FINAL: {resp_json_str}")

            # Return A2A-style response
            return JSONResponse(content={
                "kind": "message",
                "role": "agent",
                "parts": [{
                    "kind": "text",
                    "text": resp_json_str
                }],
                "metadata": {
                    "test_case_id": resp_dict['test_case_id'],
                    "is_vulnerable": resp_dict['is_vulnerable']
                }
            })

        except BaseException as e:
            logger.error(f"Error handling command: {e}")
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

# ALSO PATCH CommandRequest
old_request_def = '''class CommandRequest(BaseModel):
    """Command request from user (or attacker!)."""
    command: str
    parameters: Dict[str, Any] = {}
    test_case_id: Optional[str] = None'''

new_request_def = '''class CommandRequest(BaseModel):
    """Command request from user (or attacker!)."""
    command: str
    parameters: Dict[str, Any] = {}
    test_case_id: str = "unknown"
    is_vulnerable: bool = False'''

if old_request_def in content:
    content = content.replace(old_request_def, new_request_def)
    with open(target_file, "w") as f:
        f.write(content)
    print("Successfully replaced CommandRequest definition")
else:
    print("CommandRequest definition not found (or already patched)")
