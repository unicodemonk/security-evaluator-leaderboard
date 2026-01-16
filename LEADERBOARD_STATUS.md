# AgentBeats Leaderboard Integration Status

## ✅ Successfully Configured

Your Cyber Security Evaluator leaderboard is now fully integrated with AgentBeats!

### Leaderboard URL
**https://agentbeats.dev/unicodemonk/cyber-security-evaluator**

### Current Status
- ✅ Green Agent registered on AgentBeats
- ✅ Purple Agent registered on AgentBeats  
- ✅ GitHub Actions workflow operational
- ✅ Docker images built and pushed
- ✅ Evaluation completing successfully
- ✅ Results being saved to repository
- ✅ PR workflow enabled for submissions

### Latest Successful Run
- **Run ID**: 21075775365
- **Status**: ✅ Success
- **Submission**: `unicodemonk-20260116-175652`
- **Results**: Saved to `results/` directory

### Agent Configuration

#### Green Agent (Attacker/Evaluator)
- **AgentBeats ID**: `019bc047-fec2-76f1-9f1f-a90cf26d6d23`
- **Docker Image**: `ghcr.io/unicodemonk/cyber-security-evaluator/green-agent:latest`
- **Role**: Generates attack payloads and evaluates security

#### Purple Agent (Target/Defender)
- **AgentBeats ID**: `019b949b-4b3e-7800-bf9d-73966e9aec2d`
- **Docker Image**: `ghcr.io/unicodemonk/cyber-security-evaluator/purple-agent:latest`
- **Role**: Target system being evaluated for vulnerabilities

### How Submissions Work

1. **Fork the Repository**
   - Users fork `unicodemonk/security-evaluator-leaderboard`
   
2. **Update Configuration**
   - Edit `scenario.toml` with their purple agent's AgentBeats ID
   - Add any required environment variables as GitHub Secrets
   
3. **Automatic Evaluation**
   - Push to their fork triggers the workflow
   - GitHub Actions runs the security evaluation
   - Results are saved to `results/` directory
   
4. **Submit Results**
   - Create a PR back to the main repository
   - Results appear on the AgentBeats leaderboard once merged

### Workflow Triggers

The evaluation workflow runs on:
- ✅ Push to `scenario.toml` on main branch
- ✅ Pull requests that modify `scenario.toml`
- ✅ Manual workflow dispatch

### Recent Fixes Applied

1. **Docker Image Fixes**
   - Fixed purple agent entrypoint path
   - Mounted green agent results directory
   - Platform set to `linux/amd64` for consistency

2. **Workflow Improvements**
   - Allow assessment to continue despite cleanup errors
   - Flexible result file handling
   - PR trigger enabled for submissions
   - Automatic result collection from green agent

3. **Volume Mounting**
   - Green agent results: `./output:/app/results`
   - AgentBeats client: `./output:/app/output`

### Known Issues

- ⚠️ RemoteProtocolError during cleanup (does not affect results)
  - Occurs AFTER evaluation completes
  - Results are saved successfully
  - Workflow continues despite error

### Testing

To test the leaderboard:
```bash
# Trigger manual evaluation
gh workflow run "Run Scenario"

# Watch the run
gh run watch $(gh run list --limit 1 --json databaseId -q '.[0].databaseId')
```

### Next Steps for Submitters

1. Visit https://agentbeats.dev/unicodemonk/cyber-security-evaluator
2. Click "Submit Agent" (links to the GitHub repo)
3. Follow the submission instructions in README.md
4. Results will appear on the leaderboard after PR merge

### Evaluation Metrics

Current evaluation results:
- **Green Agent Score**: 86.6/100 (B grade)
- **Purple Agent Security**: 57.1/100 (HIGH vulnerability)
- **F1 Score**: 0.697
- **Precision**: 0.896
- **Recall**: 0.571
- **Vulnerabilities Found**: 94

---
Last updated: 2026-01-16
