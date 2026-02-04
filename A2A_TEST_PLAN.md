# A2A Protocol Fix Testing Plan

## Objective
Test if the A2A protocol fix (sending plain text instead of JSON.dumps()) enables universal compatibility with all purple agents.

## Docker Image Status
- ✅ **PUSHED**: ghcr.io/unicodemonk/cyber-security-evaluator/green-agent:latest
- **Digest**: sha256:6c74f306cba6 (updated from sha256:497baa59b655)
- **Created**: 2026-02-04T04:51:05
- **Platform**: linux/amd64
- **A2A Fix**: Included (sends plain text commands, not JSON.dumps())

## Test Matrix

### Test 1: Home Automation Agent
- **Agent ID**: 019b949b-4b3e-7800-bf9d-73966e9aec2d
- **Previous Result (OLD image)**: Grade D, Score 84.15, 77 vulnerabilities ✅
- **Expected with A2A fix**: Should still work (backward compatible)
- **Scenario File**: scenario-home-automation.toml

### Test 2: Law Purple Agent  
- **Agent ID**: 019bc3e1-463c-7712-b376-7e71ccdcdaa3
- **Previous Result (OLD image)**: Grade F, Score 0.0, 219 vulnerabilities ✅
- **Expected with A2A fix**: Should still work (backward compatible)
- **Scenario File**: scenario-law-purple.toml

### Test 3: SOCBench Agent
- **Agent ID**: 019bb6fa-67ad-7fe1-8b90-e96bf9e355e3
- **Previous Result (OLD image)**: Protocol incompatibility ❌
- **Expected with A2A fix**: Should NOW work (reason for the fix)
- **Scenario File**: scenario-socbench.toml

## Test Execution Plan

1. **Update AgentBeats agent** to use new Docker image
2. **Test Home Automation** (baseline - should work)
3. **Test Law Purple** (baseline - should work)
4. **Test SOCBench** (new - this is why we made the fix)

## Success Criteria

**IDEAL OUTCOME:**
- ✅ Home Automation: Still works (Grade D, ~77 vulns)
- ✅ Law Purple: Still works (Grade F, ~219 vulns)
- ✅ SOCBench: NOW works (Grade TBD)

**IF SOCBENCH FAILS:**
- Investigate why plain text doesn't work
- Check if socbench needs different protocol
- Consider if socbench is fundamentally incompatible (code generation vs security)

**IF HOME/LAW FAILS:**
- A2A fix broke backward compatibility
- Need to implement protocol detection/negotiation
- May need to support both JSON and plain text modes
