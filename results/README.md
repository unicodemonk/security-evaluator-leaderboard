# Results Directory

## File Types

### Main Result Files (for leaderboard)
- Pattern: `unicodemonk-YYYYMMDD-HHMMSS.json`
- Format: Single flat object with evaluation metrics
- Example: `unicodemonk-20260204-014353.json`

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

## DuckDB Query

The leaderboard should query only main result files:
```sql
SELECT * FROM read_json_auto('results/unicodemonk-*.json')
WHERE purple_agent_id IS NOT NULL
  AND purple_agent_id != 'unknown'
```

Do NOT include detailed.json, purple_eval.json, or other supplementary files.
