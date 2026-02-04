# Results Directory Structure

This directory contains evaluation results for the Security Evaluator leaderboard.

## Directory Layout

```
results/
├── unicodemonk-YYYYMMDD-HHMMSS.json    # Main result files (nested structure)
└── supplementary/                        # Detailed reports and intermediate files
    ├── *.detailed.json                  # Full evaluation details
    ├── *.purple_eval.json               # Purple agent assessment data
    ├── *.green_report.md                # Human-readable green agent report
    ├── *.purple_report.md               # Human-readable purple agent report
    └── *.flat.json                      # Legacy flattened files (archived)
```

## File Format

All main result files in `results/` (not `supplementary/`) follow the nested JSON structure required by AgentBeats DuckDB queries:

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

## Important Notes

- **ONLY** main result files should be in `results/` - supplementary files go in `supplementary/`
- Each main file contains ONE evaluation with a results array containing ONE result object
- The nested structure `{"participants": {}, "results": [...]}` is REQUIRED for AgentBeats compatibility
- DO NOT flatten to `{id, purple_agent, ...}` - this breaks the DuckDB query
- Detailed/purple_eval/report files have different structures and must be in `supplementary/`
