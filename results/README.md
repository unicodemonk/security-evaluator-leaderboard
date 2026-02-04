# Results Directory

## File Types

### Main Result Files (for leaderboard)
- Pattern: `unicodemonk-YYYYMMDD-HHMMSS.json`
- Format: `{"participants": {}, "results": [{...}]}`
- Example: `unicodemonk-20260204-014353.json`
- **Structure**: Nested with results array (required for AgentBeats DuckDB query)

### Detailed Evaluation Files
- Pattern: `*.detailed.json`
- Format: Full evaluation data with all test results
- Not used for leaderboard display

### Purple Agent Reports
- Pattern: `*.purple_eval.json`, `*.purple_report.md`
- Format: Purple agent specific data
- Not used for leaderboard display

### Green Agent Reports
- Pattern: `*.green_report.md`
- Format: Green agent specific data
- Not used for leaderboard display

## DuckDB Query Structure

AgentBeats expects the SOCBench-compatible nested format:

```json
{
  "participants": {},
  "results": [
    {
      "id": "eval_...",
      "purple_agent": "agent-name",
      "purple_agent_id": "019b...",
      "score": 84.15,
      "grade": "D",
      ...
    }
  ]
}
```

The DuckDB query accesses the `results` array from each JSON file.
Each file contains ONE evaluation with results array containing ONE result object.
