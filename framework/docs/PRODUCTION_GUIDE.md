# Production Deployment Guide

## Overview

This guide covers deploying the Security Evaluation Framework in production environments with all safety features enabled.

**✅ PRODUCTION DEPLOYMENT: Use CyberSecurityEvaluator (Green Agent)**

The production system consists of:
1. **CyberSecurityEvaluator** - Green Agent with A2A protocol (HTTP API server)
2. **UnifiedEcosystem** - Core evaluation engine (wrapped by Green Agent)
3. **Production Features** - Sandbox, Cost Optimization, Coverage Tracking

**CRITICAL**: Production deployments MUST enable all three production safety enhancements:
1. **Formal Sandbox** - Isolated execution environment (✅ enabled by default)
2. **Cost Optimization** - Budget enforcement and smart routing
3. **Coverage Tracking** - Systematic MITRE ATT&CK coverage

---

## Quick Start: Production Green Agent (Recommended)

### Start the Production Green Agent

```bash
# Terminal 1: Start CyberSecurityEvaluator
python green_agents/cybersecurity_evaluator.py \
    --host 127.0.0.1 \
    --port 9010 \
    --enable-llm  # Optional: Enable LLM features

# Terminal 2: Start your Purple Agent (detector being tested)
python your_purple_agent.py --port 8000

# Terminal 3: Submit evaluation via A2A Protocol
curl -X POST http://127.0.0.1:9010/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "purple_agent_id": "my_detector",
      "purple_agent_endpoint": "http://127.0.0.1:8000",
      "config": {
        "scenario": "sql_injection",
        "max_rounds": 10,
        "budget_usd": 50.0,
        "use_sandbox": true,
        "use_cost_optimization": true,
        "use_coverage_tracking": true
      }
    }
  }'
```

**Key Benefits:**
- ✅ A2A Protocol compliant (AgentBeats integration)
- ✅ Sandbox enabled by default
- ✅ Production-safe isolation
- ✅ Comprehensive metrics and coverage tracking

For complete usage guide, see: [green_agents/README.md](../../green_agents/README.md)

---

## Alternative: Direct Python API (Advanced)

If you prefer direct Python integration without HTTP/A2A protocol:

### Quick Start: Production-Safe Configuration

```python
from framework.ecosystem import UnifiedEcosystem
from scenarios.sql_injection import SQLInjectionScenario, SimplePatternPurpleAgent

# PRODUCTION-SAFE CONFIGURATION
config = {
    # Enhancement 5: Formal Sandbox (CRITICAL)
    'use_sandbox': True,
    'sandbox_config': {
        'image': 'python:3.10-slim',
        'cpu_limit': 0.5,              # Limit to 0.5 CPUs
        'memory_limit': '512m',         # Limit to 512MB RAM
        'timeout_seconds': 30,          # Kill after 30s
        'enable_network': False         # Block all network access
    },

    # Enhancement 6: Cost Optimization
    'use_cost_optimization': True,

    # Enhancement 7: Coverage Tracking
    'use_coverage_tracking': True,
    'taxonomy': 'MITRE_ATT&CK',

    # Agent configuration
    'num_boundary_probers': 2,
    'num_exploiters': 3,
    'num_mutators': 2,
    'num_validators': 1
}

# Create ecosystem
scenario = SQLInjectionScenario()
ecosystem = UnifiedEcosystem(
    scenario=scenario,
    use_llm=False,
    config=config
)

# Evaluate purple agent
purple_agent = SimplePatternPurpleAgent(patterns=["'", '"', 'OR', 'UNION'])

result = ecosystem.evaluate(
    purple_agent=purple_agent,
    max_rounds=10,
    budget_usd=50.0  # Optional budget limit
)

# Results
print(f"F1 Score: {result.metrics.f1_score:.3f}")
print(f"Total Cost: ${result.total_cost_usd:.2f}")
print(f"Coverage: {ecosystem.get_coverage_report()['coverage_summary']['coverage_percentage']:.1f}%")
```

---

## Enhancement 5: Formal Sandbox

### Why It's Critical

Without sandbox isolation, malicious attacks can:
- Execute arbitrary code on your server
- Exfiltrate sensitive data
- Launch network attacks
- Consume unlimited resources

### Security Layers

The sandbox provides **5 layers of protection**:

1. **Container Isolation** - Separate kernel namespace
2. **seccomp Profile** - System call filtering (blocks fork, exec, socket, etc.)
3. **Network Policies** - No external network access (default)
4. **Resource Limits** - CPU, memory, and time limits
5. **Read-Only Filesystem** - Only /tmp is writable

### Configuration Options

```python
sandbox_config = {
    'image': 'python:3.10-slim',     # Docker image
    'cpu_limit': 0.5,                 # Fraction of CPU (0.5 = 50%)
    'memory_limit': '512m',           # Memory limit
    'timeout_seconds': 30,            # Execution timeout
    'enable_network': False           # Network access (default: False)
}
```

### Testing Sandbox

Run sandbox-specific tests:

```bash
pytest tests/test_sandbox.py -v
```

### Disabled Syscalls

The seccomp profile blocks dangerous operations:

- **Network**: socket, connect, bind, listen
- **Process Creation**: fork, vfork, clone, exec
- **Dangerous Ops**: ptrace, mount, reboot, module loading

See `framework/sandbox.py:SECCOMP_PROFILE` for full list.

---

## Enhancement 6: Cost Optimization

### Features

1. **Smart Model Routing** - Routes requests to cheap/expensive LLMs based on complexity
2. **Budget Enforcement** - Phase-based budget limits with hard stops
3. **Cost Prediction** - Estimates evaluation cost before execution

### Configuration

```python
# Enable cost optimization
config = {
    'use_cost_optimization': True
}

# Provide LLM clients
from openai import OpenAI

llm_clients = [
    OpenAI(model='gpt-4'),           # Expensive, high quality
    OpenAI(model='gpt-3.5-turbo'),   # Medium cost/quality
    OpenAI(model='gpt-3.5-turbo')    # Cheap, fast
]

ecosystem = UnifiedEcosystem(
    scenario=scenario,
    use_llm=True,
    llm_clients=llm_clients,
    config=config
)

# Evaluate with budget
result = ecosystem.evaluate(
    purple_agent=purple_agent,
    max_rounds=10,
    budget_usd=100.0  # Hard limit: $100
)
```

### Phase-Based Budgets

Total budget is split across phases:
- **Exploration (40%)**: Discovery and initial testing
- **Exploitation (35%)**: Targeted attack generation
- **Validation (25%)**: Verification and reporting

### Cost Prediction

```python
# Predicts cost before evaluation
💰 Predicted cost: $75.50
⚠️  Predicted cost ($75.50) exceeds budget ($50.00)
   Evaluation may terminate early due to budget constraints
```

### Model Routing

- **Simple tasks** (yes/no, pattern matching) → Cheap model
- **Complex tasks** (creative generation, analysis) → Expensive model
- **Adaptive learning** - Routes based on historical performance

### Testing Cost Optimization

```bash
pytest tests/test_cost_optimizer.py -v
```

---

## Enhancement 7: Coverage Tracking

### Purpose

Systematically tracks MITRE ATT&CK coverage to:
- Identify gaps in evaluation scenarios
- Prioritize next techniques to implement
- Generate scenario templates automatically

### Configuration

```python
config = {
    'use_coverage_tracking': True,
    'taxonomy': 'MITRE_ATT&CK'  # or 'OWASP_Top_10'
}
```

### Coverage Levels

- **Covered (10+ tests)**: Green ✅
- **Partially Covered (3-9 tests)**: Yellow ⚠️
- **Uncovered (0-2 tests)**: Red ❌

### Usage

#### 1. Get Coverage Report

```python
coverage_report = ecosystem.get_coverage_report()

print(f"Coverage: {coverage_report['coverage_summary']['coverage_percentage']:.1f}%")
print(f"Covered: {coverage_report['coverage_summary']['covered']}")
print(f"Uncovered: {coverage_report['coverage_summary']['uncovered']}")
```

#### 2. Get Next Scenario Suggestion

```python
suggestion = ecosystem.suggest_next_scenario()

print(f"Suggested Technique: {suggestion['suggested_technique']}")
print(f"Priority Score: {suggestion['priority_score']:.2f}")
print(f"Coverage Impact: {suggestion['coverage_impact']} techniques")
```

#### 3. Generate Scenario Template

```python
template = ecosystem.generate_scenario_template('T1059')

# Save template
with open('t1059_scenario.py', 'w') as f:
    f.write(template)
```

### CLI Tool

Use the coverage CLI for quick coverage checks:

```bash
# Show coverage report
python -m framework.coverage_cli report sql_injection

# Get next scenario suggestion
python -m framework.coverage_cli suggest sql_injection --json suggestion.json

# Generate scenario template
python -m framework.coverage_cli template T1059 -o t1059_scenario.py
```

### Testing Coverage Tracking

```bash
pytest tests/test_coverage_tracker.py -v
```

---

## Running All Tests

Run the comprehensive test suite:

```bash
# All tests
pytest tests/ -v

# Specific enhancement
pytest tests/test_sandbox.py -v
pytest tests/test_cost_optimizer.py -v
pytest tests/test_coverage_tracker.py -v

# Integration tests (all enhancements together)
pytest tests/test_production_integration.py -v
```

**Test Coverage**:
- Sandbox: 11 tests
- Cost Optimization: 17 tests
- Coverage Tracking: 19 tests
- Integration: 15 tests
- **Total: 62 comprehensive tests**

---

## Deployment Checklist

Before deploying to production:

- [ ] **Sandbox enabled** (`use_sandbox=True`)
- [ ] **Docker installed** and accessible
- [ ] **Resource limits** configured appropriately
- [ ] **Network access** disabled (unless required)
- [ ] **Budget limits** set (if using LLMs)
- [ ] **Coverage tracking** enabled
- [ ] **All tests passing** (`pytest tests/ -v`)
- [ ] **Logging configured** (capture warnings)
- [ ] **Monitoring setup** (cost, performance, errors)

---

## Security Best Practices

### 1. Always Use Sandbox in Production

```python
# ❌ NEVER do this in production
config = {'use_sandbox': False}

# ✅ Always do this in production
config = {'use_sandbox': True}
```

### 2. Set Budget Limits

```python
# ✅ Always set budget when using LLMs
result = ecosystem.evaluate(
    purple_agent=purple_agent,
    max_rounds=10,
    budget_usd=100.0  # Hard limit
)
```

### 3. Monitor Logs for Warnings

```python
import logging

logging.basicConfig(level=logging.INFO)

# Watch for these warnings:
# ⚠️  NOT production-safe
# ⚠️  Predicted cost exceeds budget
# ⚠️  Docker not available
```

### 4. Regular Security Audits

```bash
# Review seccomp profile
cat framework/sandbox.py | grep -A 50 "SECCOMP_PROFILE"

# Check for sandbox bypasses
pytest tests/test_sandbox.py::test_sandbox_network_isolation -v
```

---

## Troubleshooting

### Docker Not Available

**Error**: `Docker not available: [Errno 2] No such file or directory`

**Solution**:
1. Install Docker: `https://docs.docker.com/get-docker/`
2. Start Docker daemon
3. Verify: `docker --version`

### Sandbox Timeout

**Error**: Container timeout after 30s

**Solution**:
```python
sandbox_config = {
    'timeout_seconds': 60  # Increase timeout
}
```

### High Costs with LLMs

**Error**: Predicted cost exceeds budget

**Solution**:
1. Enable cost optimization: `use_cost_optimization=True`
2. Reduce rounds: `max_rounds=5`
3. Increase budget: `budget_usd=200.0`

### Missing Coverage Data

**Error**: `Coverage tracking not enabled`

**Solution**:
```python
config = {'use_coverage_tracking': True}
```

---

## Performance Tuning

### Adjust Agent Count

```python
config = {
    'num_boundary_probers': 1,  # Min: 1, Default: 2
    'num_exploiters': 2,        # Min: 1, Default: 3
    'num_mutators': 1,          # Min: 1, Default: 2
    'num_validators': 1         # Min: 1, Default: 1
}
```

**More agents = Better coverage, Higher cost**

### Adjust Sandbox Resources

```python
sandbox_config = {
    'cpu_limit': 1.0,          # More CPU = Faster execution
    'memory_limit': '1g',      # More RAM = Handle larger attacks
    'timeout_seconds': 60      # Longer timeout = More complex tests
}
```

### Adjust Evaluation Parameters

```python
result = ecosystem.evaluate(
    purple_agent=purple_agent,
    max_rounds=20,              # More rounds = Better coverage
    budget_usd=200.0            # Higher budget = More LLM usage
)
```

---

## Support

For issues or questions:
- GitHub Issues: `https://github.com/yourrepo/SecurityEvaluator/issues`
- Documentation: `docs/`
- Tests: `tests/`

---

## License

See LICENSE file.
