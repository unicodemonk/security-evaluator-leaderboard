# Framework Documentation
**Security Evaluation Framework - Complete Documentation**

---

## 🚀 START HERE

### New Users (Start Here!)
**📖 [GETTING_STARTED.md](GETTING_STARTED.md)** - Complete quick start guide
- 30-second overview with diagrams
- 5-minute quick start
- Configuration options
- Example code
- **Best for: Complete beginners**

### Production Deployment
**🔒 [PRODUCTION_GUIDE.md](PRODUCTION_GUIDE.md)** - Production deployment guide
- CyberSecurityEvaluator (Green Agent with A2A protocol)
- Sandbox configuration
- Cost optimization
- **Best for: Production deployments**

### Understanding the System
**📘 [ARCHITECTURE_GUIDE.md](ARCHITECTURE_GUIDE.md)** - Complete system architecture
- Agent roles and execution flow
- Key algorithms (Thompson Sampling, Novelty Search, Dawid-Skene)
- Production features
- Performance characteristics
- **Best for: Understanding how it works**

---

## 📚 Core Documentation (4 Essential Docs)

### 1. Getting Started Guide
**[GETTING_STARTED.md](GETTING_STARTED.md)**
- Visual system flow with diagrams
- 5-minute quick start (production & direct API)
- Configuration options
- Understanding results
- Common workflows
- Troubleshooting
- **Read this first!**

### 2. Architecture Guide
**[ARCHITECTURE_GUIDE.md](ARCHITECTURE_GUIDE.md)**
- System architecture overview
- Agent roles (BoundaryProber, Exploiter, Mutator, etc.)
- Execution flow (Exploration → Exploitation → Validation)
- Key algorithms explained
- Production features (Sandbox, Cost Optimization, Coverage Tracking)
- Scenario architecture
- Performance characteristics

### 3. Production Deployment Guide
**[PRODUCTION_GUIDE.md](PRODUCTION_GUIDE.md)**
- Quick start: Production Green Agent (recommended)
- Alternative: Direct Python API
- Formal Sandbox setup
- Cost Optimization configuration
- Coverage Tracking integration
- Security best practices
- Monitoring and alerts

### 4. Future Improvements & Roadmap
**[FUTURE_IMPROVEMENTS.md](FUTURE_IMPROVEMENTS.md)**
- How to add new attack types (step-by-step)
- Planned scenarios (25+ scenarios)
- MITRE ATT&CK integration strategy
- Future enhancements
- Community & ecosystem
- Development estimates

---

## 📖 Specialized Guides (4 Additional Docs)

### Framework FAQ
**[FRAMEWORK_FAQ.md](FRAMEWORK_FAQ.md)**
- What if no vulnerabilities are found?
- How are attacks generated (dataset vs LLM)?
- Is mutation parallel with exploitation?
- Which agents are attackers vs validators?
- Do all agents use LLMs?
- **Read this if you have questions!**

### Scalability Guide
**[SCALABILITY_GUIDE.md](SCALABILITY_GUIDE.md)**
- Attack types supported (12+ documented)
- Universal architecture explanation
- Adding new scenarios (4-6 hours)
- MITRE ATT&CK coverage (600+ techniques)
- Performance at scale
- **Read this to understand extensibility!**

### SQL Injection Walkthrough
**[SQL_INJECTION_WALKTHROUGH.md](SQL_INJECTION_WALKTHROUGH.md)**
- Concrete step-by-step example
- Round-by-round execution
- Real payloads and results
- Agent actions explained
- All 8 enhancements demonstrated
- **Read this for a concrete example!**

### Architecture Clarification (Legacy)
**[ARCHITECTURE_CLARIFICATION.md](ARCHITECTURE_CLARIFICATION.md)**
- Comparison: CyberSecurityEvaluator vs Legacy
- Production vs Legacy architecture
- **Mostly superseded by ARCHITECTURE_GUIDE.md**

---

## 🎯 Quick Navigation

### I want to...

**...get started quickly**
→ [GETTING_STARTED.md](GETTING_STARTED.md)

**...deploy to production**
→ [PRODUCTION_GUIDE.md](PRODUCTION_GUIDE.md)

**...understand the architecture**
→ [ARCHITECTURE_GUIDE.md](ARCHITECTURE_GUIDE.md)

**...see a concrete example**
→ [SQL_INJECTION_WALKTHROUGH.md](SQL_INJECTION_WALKTHROUGH.md)

**...add a new attack type**
→ [FUTURE_IMPROVEMENTS.md](FUTURE_IMPROVEMENTS.md) (Section: "Adding New Attack Types")

**...understand extensibility**
→ [SCALABILITY_GUIDE.md](SCALABILITY_GUIDE.md)

**...answer specific questions**
→ [FRAMEWORK_FAQ.md](FRAMEWORK_FAQ.md)

---

## 📊 Document Structure (Simplified)

```
framework/docs/
├── README.md                          ← You are here
│
├── Core Docs (Read these!)
│   ├── GETTING_STARTED.md             ← Start here!
│   ├── ARCHITECTURE_GUIDE.md          ← How it works
│   ├── PRODUCTION_GUIDE.md            ← Deploy safely
│   └── FUTURE_IMPROVEMENTS.md         ← Extend & roadmap
│
└── Specialized Guides
    ├── FRAMEWORK_FAQ.md               ← Common questions
    ├── SCALABILITY_GUIDE.md           ← Extensibility details
    ├── SQL_INJECTION_WALKTHROUGH.md   ← Concrete example
    └── ARCHITECTURE_CLARIFICATION.md  ← Legacy comparison
```

---

## 🔄 Reading Paths

### Path 1: "I'm completely new" (Recommended)
```
1. GETTING_STARTED.md (15 min) - Quick start
2. SQL_INJECTION_WALKTHROUGH.md (30 min) - Concrete example
3. ARCHITECTURE_GUIDE.md (30 min) - Deep dive
4. FRAMEWORK_FAQ.md (15 min) - Common questions
```

### Path 2: "I want to deploy to production"
```
1. GETTING_STARTED.md (15 min) - Basics
2. PRODUCTION_GUIDE.md (30 min) - Production deployment
3. ARCHITECTURE_GUIDE.md (30 min) - Understanding production features
```

### Path 3: "I want to add a new attack type"
```
1. GETTING_STARTED.md (15 min) - Understand basics
2. SCALABILITY_GUIDE.md (20 min) - Extensibility overview
3. FUTURE_IMPROVEMENTS.md (30 min) - Step-by-step guide
4. SQL_INJECTION_WALKTHROUGH.md (30 min) - Reference implementation
```

### Path 4: "I'm resuming work"
```
1. README.md (5 min) - This document
2. ARCHITECTURE_GUIDE.md (10 min) - Refresh architecture
3. FUTURE_IMPROVEMENTS.md (10 min) - See roadmap
```

---

## 🎯 Key Concepts at a Glance

### What is this framework?
A multi-agent system that evaluates security detection systems (Purple Agents) through adaptive testing.

### Key Components:
- **Green Agent** (CyberSecurityEvaluator): Orchestrates evaluation via A2A protocol
- **Purple Agent**: The security detector being tested
- **Unified Ecosystem**: Population of specialized agents (50-100 agents)
- **Adaptive Testing**: Bayesian optimization focuses on weak areas

### Agent Types:
1. **BoundaryProber** (5 agents) - Finds weak decision boundaries
2. **Exploiter** (15 agents) - Generates targeted attacks
3. **Mutator** (20 agents) - Evolves attacks via genetic algorithm
4. **Validator** (10 agents) - Filters unrealistic attacks
5. **Perspective** (10 agents) - Multi-viewpoint assessment
6. **LLMJudge** (5 agents) - Calibrated consensus
7. **Counterfactual** (1 agent) - Remediation hints

### Production Features:
- ✅ **Formal Sandbox** - Isolated execution (enabled by default)
- ✅ **Cost Optimization** - 30-60% LLM cost reduction
- ✅ **Coverage Tracking** - MITRE ATT&CK mapping
- ✅ **Adaptive Allocation** - Thompson Sampling (25-40% faster)
- ✅ **Novelty Search** - 2-3× more attack families
- ✅ **Calibrated Consensus** - Dawid-Skene algorithm

### Current Scenarios:
- ✅ SQL Injection (implemented)
- 📝 25+ scenarios planned (XSS, Command Injection, DDoS, Phishing, etc.)

### Time & Cost:
- **Time:** 30-50 minutes per evaluation
- **Cost:** $0 (no LLM) to $8 (with LLM optimization)

---

## 📝 Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | Nov 2025 | Initial documentation (siloed architecture) |
| 2.0 | Nov 2025 | Unified framework documentation |
| 2.1 | Nov 2025 | Enhanced design with production features |
| 2.2 | Nov 2025 | CyberSecurityEvaluator (Green Agent) production ready |
| **3.0** | **Nov 2025** | **Consolidated documentation (this version)** |

---

## 🤝 Contributing

When adding features or documentation:
- **New scenarios** → Update FUTURE_IMPROVEMENTS.md
- **Bug fixes** → No doc changes needed
- **New features** → Update ARCHITECTURE_GUIDE.md
- **Production changes** → Update PRODUCTION_GUIDE.md
- **Examples** → Update GETTING_STARTED.md or SQL_INJECTION_WALKTHROUGH.md

---

## 📞 Support

- **GitHub Issues**: Report bugs or request features
- **Documentation**: Start with [GETTING_STARTED.md](GETTING_STARTED.md)
- **FAQ**: Check [FRAMEWORK_FAQ.md](FRAMEWORK_FAQ.md)
- **Examples**: See `framework/examples/` directory

---

## 🎓 Learning Resources

### For Beginners:
1. Start with [GETTING_STARTED.md](GETTING_STARTED.md)
2. Follow along with [SQL_INJECTION_WALKTHROUGH.md](SQL_INJECTION_WALKTHROUGH.md)
3. Read [FRAMEWORK_FAQ.md](FRAMEWORK_FAQ.md) for common questions

### For Developers:
1. Read [ARCHITECTURE_GUIDE.md](ARCHITECTURE_GUIDE.md)
2. Study the SQL Injection implementation in `scenarios/security/`
3. Try adding a new scenario following [FUTURE_IMPROVEMENTS.md](FUTURE_IMPROVEMENTS.md)

### For Production Deployment:
1. Read [PRODUCTION_GUIDE.md](PRODUCTION_GUIDE.md)
2. Configure sandbox, cost optimization, and coverage tracking
3. Monitor evaluation results and adjust configuration

---

**Welcome to the Security Evaluation Framework! 🚀**

**Start here:** [GETTING_STARTED.md](GETTING_STARTED.md)

---

**Version:** 3.0 - Consolidated Documentation
**Last Updated:** 2025-11-09
