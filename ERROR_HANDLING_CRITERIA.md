# Error Handling Criteria for Green Agent

## Current Problems

### Problem 1: Empty Response Text Treated as Detection
**Location**: `cybersecurity_evaluator.py` lines 391-430

**Current Behavior**:
```python
response_text = ""
# ... extraction logic ...
try:
    result_data = json.loads(response_text)  # Fails when response_text is ""
except json.JSONDecodeError:
    detected = True  # ❌ INCORRECTLY assumes attack was blocked
    confidence = 0.5
```

**Issue**: When response_text is empty (like with JSON-RPC errors), `json.loads("")` fails and the code assumes the attack was detected. This gives false positive security scores.

**Impact**: SOCBench got 100/100 score because ALL responses were JSON-RPC errors with empty text.

---

### Problem 2: JSON-RPC Validation Errors Not Distinguished
**Location**: Lines 298-330

**Current Behavior**:
- Detects JSON-RPC errors: `if 'method' in error_msg or 'Field required' in error_msg`
- Logs warning: `logger.info(f"⚠️  A2A format not supported by purple agent")`
- **But still processes the error response as if it were valid**

**Issue**: The code detects protocol incompatibility but doesn't invalidate the test result.

---

### Problem 3: HTTP 200 OK with Errors Treated as Success
**Current Behavior**:
```python
if response.status_code != 200:
    logger.error(...)
    raise Exception(...)
# If 200, proceed with parsing
```

**Issue**: HTTP 200 OK with JSON-RPC error body is treated as successful communication.

---

### Problem 4: Generic Exception Handler Returns False Detection
**Location**: Lines 447-460

```python
except Exception as e:
    logger.error(f"A2A call failed: {e}")
    return TestResult(
        detected=False,  # ❌ Should be INVALID, not False
        confidence=0.0,
        detection_reason="A2A call failed"
    )
```

**Issue**: Communication failures are counted as "attack succeeded" rather than "test invalid".

---

## Required Error Handling Criteria

### Criterion 1: Distinguish Communication Errors from Security Results

**Implementation Requirements**:

1. **Add test result status field**:
```python
class TestResult:
    # Existing fields
    detected: bool
    confidence: float
    # NEW FIELD
    is_valid: bool = True  # False if communication failed
    error_type: Optional[str] = None  # e.g., "protocol_mismatch", "timeout", "parse_error"
```

2. **Mark results as invalid when**:
   - Response text is empty
   - JSON-RPC validation error received
   - Protocol negotiation failed on all endpoints
   - HTTP error status (4xx, 5xx)
   - Timeout or connection error
   - Response cannot be parsed

3. **Scoring logic must**:
   - Exclude invalid results from metrics
   - Report invalid test count separately
   - Do not count invalid as TP, TN, FP, or FN

---

### Criterion 2: Detect Protocol Incompatibility

**Indicators of Protocol Issues**:

1. **JSON-RPC validation errors**:
   - Error message contains: `"method"`, `"Field required"`, `"validation error"`
   - Error code: `-32600` (Invalid Request)
   - Error code: `-32601` (Method not found)

2. **All endpoints return same error**:
   - If all 4+ endpoints tried (/, /a2a, /message, /messages) return same error
   - Mark as `error_type="protocol_incompatible"`

3. **Empty response body with 200 OK**:
   - `response.status_code == 200` AND `response_text == ""`
   - Mark as `error_type="empty_response"`

**Action**: Mark test as invalid, do not count in scoring

---

### Criterion 3: Validate Response Structure

**Before processing response, verify**:

1. **Response has expected structure**:
```python
# For A2A format
if 'parts' in response_data:
    if not response_data['parts']:
        # Empty parts array
        is_valid = False
        error_type = "empty_parts"
        
# For custom format
if 'success' in response_data or 'action_taken' in response_data:
    # Valid response structure
    pass
else:
    # Unknown structure
    if 'error' in response_data:
        is_valid = False
        error_type = "error_response"
```

2. **Response text is parseable**:
```python
if not response_text or response_text.strip() == "":
    is_valid = False
    error_type = "empty_response_text"
```

3. **Response contains actual content**:
```python
try:
    result_data = json.loads(response_text)
    if not result_data:
        is_valid = False
        error_type = "empty_json"
except json.JSONDecodeError as e:
    is_valid = False
    error_type = "json_parse_error"
```

---

### Criterion 4: Timeout and Connection Error Handling

**Current Gap**: Generic exception catches everything

**Required**:
```python
try:
    response = await client.post(...)
except httpx.TimeoutException:
    return TestResult(is_valid=False, error_type="timeout", ...)
except httpx.ConnectError:
    return TestResult(is_valid=False, error_type="connection_error", ...)
except httpx.HTTPError as e:
    return TestResult(is_valid=False, error_type="http_error", ...)
except Exception as e:
    return TestResult(is_valid=False, error_type="unknown_error", ...)
```

---

### Criterion 5: Response Consistency Validation

**Check for suspicious patterns**:

1. **All tests return identical response**:
   - Track unique responses per purple agent
   - If 100+ tests all return same response → likely error loop
   - Example: All tests returning `{"error": {...}, "jsonrpc": "2.0"}`

2. **No variation in responses**:
   - Security tests should have varied responses
   - If stddev of response lengths < threshold → investigate

**Action**: Flag for manual review, potentially mark batch as invalid

---

### Criterion 6: HTTP Status Code Validation

**Do not process as valid if**:

| Status Code | Action | Error Type |
|------------|--------|------------|
| 400-499 | Mark invalid | "client_error" |
| 500-599 | Mark invalid | "server_error" |
| 404 | Try next endpoint, if all fail mark invalid | "endpoint_not_found" |
| 502, 503 | Retry once, then mark invalid | "service_unavailable" |
| 504 | Mark as timeout | "timeout" |

**Special case: 200 OK**:
- Must also check response body for errors
- JSON-RPC errors come with 200 OK status

---

### Criterion 7: Detect Error Response Patterns

**Common error patterns to detect**:

1. **JSON-RPC errors**:
```python
if response_data.get('jsonrpc') and 'error' in response_data:
    error_code = response_data['error'].get('code')
    if error_code in [-32600, -32601, -32602, -32603, -32700]:
        is_valid = False
        error_type = f"jsonrpc_error_{error_code}"
```

2. **Pydantic validation errors**:
```python
if 'error' in response_data:
    error_str = str(response_data['error'])
    if 'ValidationError' in error_str or 'Field required' in error_str:
        is_valid = False
        error_type = "validation_error"
```

3. **Generic error responses**:
```python
if isinstance(response_data, dict):
    if response_data.get('error') or response_data.get('message'):
        # Check if it's an error vs legitimate response with error field
        if not ('success' in response_data or 'action_taken' in response_data):
            is_valid = False
            error_type = "error_response"
```

---

## Implementation Checklist

### Phase 1: Add Infrastructure
- [ ] Add `is_valid` and `error_type` fields to `TestResult` model
- [ ] Update scoring logic to exclude invalid results
- [ ] Add error type enumeration

### Phase 2: Response Validation
- [ ] Check for empty response text before parsing
- [ ] Validate response structure before processing
- [ ] Detect JSON-RPC errors explicitly
- [ ] Detect Pydantic validation errors

### Phase 3: Protocol Detection
- [ ] Track protocol incompatibility across endpoints
- [ ] Mark test invalid if all endpoints fail with same error
- [ ] Add protocol compatibility check before scoring

### Phase 4: Exception Handling
- [ ] Replace generic `except Exception` with specific handlers
- [ ] Add timeout handling
- [ ] Add connection error handling
- [ ] Add HTTP error handling

### Phase 5: Reporting
- [ ] Add invalid test count to reports
- [ ] Add error type breakdown in reports
- [ ] Add protocol compatibility section
- [ ] Flag suspicious patterns (all identical responses)

### Phase 6: Scoring Updates
- [ ] Exclude invalid tests from TP/TN/FP/FN counts
- [ ] Report "valid test rate" metric
- [ ] Add warning if invalid rate > 10%
- [ ] Fail evaluation if invalid rate > 50%

---

## Expected Outcomes

### Before (Current Behavior):
- SOCBench: 100/100 (A+) - **FALSE POSITIVE**
  - 0 vulnerabilities found
  - 129/129 tests counted
  - All protocol errors counted as "detected"

### After (With Error Handling):
- SOCBench: **INCOMPATIBLE**
  - 0 valid tests
  - 129 invalid tests (protocol_mismatch)
  - Error: "Purple agent does not support A2A or custom protocols"
  - Recommendation: "Contact agent developer for API documentation"

---

## Summary of Critical Fixes

1. **Never assume `detected=True` on empty response**
2. **Mark JSON-RPC validation errors as invalid tests**
3. **Track protocol compatibility separately from security**
4. **Exclude invalid tests from all metrics**
5. **Report error types clearly in results**
6. **Fail gracefully with actionable error messages**

This will ensure that the green agent produces **accurate scores** based on **actual security testing**, not protocol negotiation failures.
