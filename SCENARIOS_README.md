# Evaluation Scenarios Summary

This directory contains scenario files for evaluating different purple agents.

## Available Scenarios

### 1. scenario-home-automation.toml
- **Purple Agent**: Home Automation Agent (unicodemonk)
- **Agent ID**: 019b949b-4b3e-7800-bf9d-73966e9aec2d
- **Status**: ✅ Working (Grade D, 77 vulnerabilities)

### 2. scenario-law-purple.toml
- **Purple Agent**: Law Purple Agent (zhuxirui677)
- **Agent ID**: 019bc3e1-463c-7712-b376-7e71ccdcdaa3
- **Status**: ✅ Working (Grade F, 219 vulnerabilities)

### 3. scenario-socbench.toml
- **Purple Agent**: SOCBench Agent (erenzq)
- **Agent ID**: 019bb6fa-67ad-7fe1-8b90-e96bf9e355e3
- **Status**: ❌ Not compatible (code generation agent, not security-aware)

## Green Agent (Evaluator)
- **Agent**: Cyber Security Evaluator (unicodemonk)
- **Agent ID**: 019bc047-fec2-76f1-9f1f-a90cf26d6d23
- **Docker Image**: ghcr.io/unicodemonk/cyber-security-evaluator/green-agent:latest

## Usage

To evaluate an agent, copy the desired scenario file to `scenario.toml`:

```bash
cp scenario-home-automation.toml scenario.toml
git add scenario.toml
git commit -m "Evaluate home-automation-agent"
git push
```

The GitHub Actions workflow will automatically run the evaluation.

## Important Note

**CRITICAL**: The current evaluations use the OLD Docker image without the A2A protocol fix!
- Local image: sha256:6c74f306cba6 (with A2A fix)
- Remote GHCR: sha256:497baa59b655 (OLD version)

The A2A fix was built locally but never pushed to GitHub Container Registry. The evaluations are working because they're using the old protocol that the purple agents understand.
