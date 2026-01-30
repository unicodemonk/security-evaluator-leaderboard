# Protocol Discovery & A2A Endpoint Routing

## Problem Discovered

SOCBench (and potentially other purple agents on AgentBeats) uses the `a2a.server` framework which supports MULTIPLE protocol handlers:
- **JSON-RPC handler** at `/`
- **A2A handler** at `/a2a` or `/message` (or possibly root)

### The Issue
When both handlers are configured, the JSON-RPC handler validates ALL POST requests first. When it receives an A2A message (which lacks the `method` field required by JSON-RPC), it returns a validation error:

```
ValidationError: 1 validation error for JSONRPCRequest
  method: Field required
```

This happens BEFORE the request reaches the A2A handler.

## Root Cause

AgentBeats agents may mount A2A at different paths:
- Root: `/` (if JSON-RPC not used)
- Standard: `/a2a`
- Alternative: `/message` or `/messages`

The green agent was only trying `/`, which hits the JSON-RPC validator in SOCBench.

## Solution Implemented

### 1. Multi-Endpoint A2A Discovery
The green agent now tries multiple standard A2A endpoints in order:
```python
a2a_endpoints = [
    "",         # Root endpoint
    "/a2a",     # Standard A2A path
    "/message",  # Alternative path
    "/messages"  # Another variant
]
```

### 2. Agent Card Discovery
Query `.well-known/agent-card.json` to discover:
- Preferred transport protocol
- Supported endpoints (future enhancement)
- Capabilities and skills

### 3. Intelligent Protocol Detection
- Try A2A on each standard endpoint
- Detect JSON-RPC validation errors and skip
- Identify successful A2A responses by structure (`parts`, `result`, `success` fields)
- Cache successful endpoint for future requests

### 4. Fallback to Protocol Patterns
If no A2A endpoint works, try common custom formats:
- Direct `{command, parameters}` 
- Text-only `{text: "..."}`
- Prompt-based `{prompt: "...", metadata: {}}`

## Benefits

✅ **Universal Compatibility**: Works with ANY purple agent that supports A2A
✅ **No Hardcoding**: Discovers the correct endpoint dynamically  
✅ **AgentBeats Compliant**: Follows the platform's A2A standard
✅ **Graceful Degradation**: Falls back to custom protocols if needed
✅ **Performance**: Caches discovered endpoints to avoid redundant discovery

## Testing Recommendations

1. **Test with SOCBench**: Verify `/a2a` endpoint works
2. **Test with home automation agent**: Verify root `/` still works
3. **Test with future agents**: Ensure discovery works for new agents
4. **Monitor logs**: Check which endpoint is discovered for each agent

## Agent Card Enhancement Needed

Purple agents SHOULD expose their A2A endpoint in the agent card:
```json
{
  "name": "My Agent",
  "preferredTransport": "A2A",
  "endpoints": {
    "a2a": "/a2a",
    "jsonrpc": "/"
  }
}
```

This would eliminate the need for endpoint probing.
