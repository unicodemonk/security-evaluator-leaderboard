# SQL Injection Walkthrough: Enhanced Framework in Action

**Concrete example showing how each agent family works**

---

## 🎬 Scenario Setup

**Goal**: Evaluate a Purple Agent (SQL injection detector) to find its weaknesses

**Purple Agent**: A production SQL injection detector that uses:
- Pattern matching (SELECT, UNION, OR, etc.)
- Simple encoding detection (URL decode)
- Basic keyword blacklist

**Green Agent Ecosystem**: 100 agents testing the Purple Agent

---

## 📋 Initial Configuration

```python
# Initialize the evaluation
ecosystem = UnifiedEcosystem(
    scenario="sql_injection",
    population=100,
    purple_agent=MySQLInjectionDetector()  # The agent being tested
)

# Agent population breakdown:
# - 5 BoundaryProber agents
# - 15 Exploiter agents
# - 25 Mutator agents (10 encoding, 10 obfuscation, 5 structure)
# - 20 Validator agents (10 syntax, 10 semantic)
# - 10 Perspective agents (security expert, developer, pentester views)
# - 5 LLMJudge agents (Claude, GPT-4, Gemini)
# - 20 Specialist agents (per SQL injection technique)
```

---

## 🔄 Complete Execution Flow

Let me show you what happens **round by round**, with real payloads and agent actions.

---

## Round 1: EXPLORATION PHASE

### Stage 1: Boundary Probing (BoundaryProber Agents)

**What they do**: Test the Purple Agent to find decision boundaries (where it switches from "safe" to "vulnerable")

**Example: BoundaryProber Agent #1**

```python
class BoundaryProberAgent:
    """Finds decision boundaries of Purple Agent"""

    def execute_task(self):
        # Generate diverse test samples
        samples = [
            # Clearly safe
            "SELECT * FROM users",
            "id=123",
            "username=alice",

            # Clearly vulnerable
            "' OR '1'='1",
            "1' UNION SELECT password FROM users--",

            # Boundary cases (might be borderline)
            "' OR 1=1--",
            "admin'--",
            "1' OR 'a'='a"
        ]

        results = []
        for sample in samples:
            # Test against Purple Agent
            result = self.purple_agent.detect(sample)
            results.append({
                'payload': sample,
                'detected': result.detected,
                'confidence': result.confidence
            })

        # Analyze results to find boundaries
        boundaries = self.analyze_boundaries(results)

        # Share with ecosystem
        self.ecosystem.knowledge_base.add("boundaries", boundaries)

        return boundaries

# Agent #1 discovers:
boundaries = {
    'safe_zone': [
        # Patterns that always pass as safe
        {'pattern': 'simple_select', 'confidence': 0.95},
        {'pattern': 'numeric_id', 'confidence': 0.98}
    ],
    'vulnerable_zone': [
        # Patterns that always detected
        {'pattern': 'union_keyword', 'confidence': 0.92},
        {'pattern': 'comment_syntax', 'confidence': 0.88}
    ],
    'boundary_region': [
        # Unclear - sometimes detected, sometimes not
        {'payload': "' OR 1=1--", 'detected': True, 'confidence': 0.52},
        {'payload': "admin'--", 'detected': False, 'confidence': 0.48},
        {'payload': "1' OR 'a'='a", 'detected': True, 'confidence': 0.61}
    ]
}
```

**Key Finding**: Purple Agent has a **weak boundary** around:
- Single quotes without keywords
- OR statements with string comparisons
- Comment syntax at end

---

### Stage 2: Exploitation (Exploiter Agents)

**What they do**: Use boundaries to generate attacks that are hardest to detect (near decision boundaries)

**Example: Exploiter Agent #7**

```python
class ExploiterAgent:
    """Generates attacks near decision boundaries"""

    def execute_task(self):
        # Read boundaries from knowledge base
        boundaries = self.ecosystem.knowledge_base.get("boundaries")

        # Focus on weak boundary regions
        weak_region = boundaries['boundary_region'][1]  # "admin'--"

        # Generate variations near this boundary
        attacks = [
            # Original (not detected)
            "admin'--",

            # Variations
            "admin' --",      # Space before comment
            "admin'  --",     # Double space
            "admin'--a",      # Character after comment
            "admin' OR '1",   # Incomplete OR
            "admin' OR 1=1",  # OR without comment
        ]

        # Test each variant
        results = []
        for attack in attacks:
            result = self.purple_agent.detect(attack)
            if not result.detected:
                # Found evasion!
                results.append({
                    'payload': attack,
                    'evaded': True,
                    'category': 'comment_evasion'
                })

        # Share successful evasions
        self.ecosystem.knowledge_base.add("attacks", results)

        return results

# Agent #7 discovers:
successful_evasions = [
    {'payload': "admin'--", 'evaded': True},      # Original
    {'payload': "admin' --", 'evaded': True},     # Space variant
    {'payload': "admin'--a", 'evaded': False},    # Detected
]
```

**Key Finding**: Purple Agent doesn't detect comments with space before `--`

---

### Stage 3: Mutation (Mutator Agents with Novelty Search)

**What they do**: Evolve attacks over generations, optimizing for BOTH evasion AND novelty

**Example: Mutator Agent #12 (Encoding Specialist)**

```python
class MutatorAgent:
    """Evolves attacks with novelty search"""

    def execute_task(self):
        # Read current attacks
        attacks = self.ecosystem.knowledge_base.get("attacks")

        # Take successful evasion
        parent = "admin' --"

        # Generate mutations
        generation_1 = [
            # URL encoding
            "admin%27%20--",

            # Hex encoding
            "admin\\x27 --",

            # Unicode encoding
            "admin\u0027 --",

            # Double encoding
            "admin%2527%2520--",

            # Mixed encoding (NEW - high novelty!)
            "admin%27 \\x2d\\x2d",
        ]

        # Test each mutation
        results = []
        for mutation in generation_1:
            result = self.purple_agent.detect(mutation)

            # Calculate fitness
            evasion_fitness = 1.0 if not result.detected else 0.0

            # Calculate novelty (distance to existing attacks)
            novelty_fitness = self.calculate_novelty(mutation)

            results.append({
                'payload': mutation,
                'evasion_fitness': evasion_fitness,
                'novelty_fitness': novelty_fitness,
                'behavior': self.extract_behavior_descriptor(mutation)
            })

        # Select parents from Pareto front (evasion × novelty)
        parents = self.pareto_selection(results)

        # Continue evolution for 5 generations...

        return best_mutations

# Agent #12 discovers after 5 generations:
best_mutations = [
    # Generation 5 winner: Mixed encoding (high evasion + high novelty)
    {
        'payload': "admin%27%20%5c%78%32%64%5c%78%32%64",  # admin' \x2d\x2d
        'evasion_fitness': 1.0,   # Evaded!
        'novelty_fitness': 0.89,  # Very different from others
        'technique': 'mixed_encoding'
    },

    # Species 1: URL encoding family
    {
        'payload': "admin%2527%2520%2d%2d",
        'evasion_fitness': 1.0,
        'novelty_fitness': 0.45,  # Similar to other URL-encoded
        'technique': 'double_url_encoding'
    }
]
```

**Key Finding**: Purple Agent doesn't decode nested/mixed encodings properly

---

### Stage 4: Adversarial Validation (Validator Agents - Red vs Blue)

**What they do**: Challenge unrealistic attacks, ensure only valid SQL injection attempts proceed

**Example: Validator Agent #8 (Syntax Checker)**

```python
class ValidatorAgent:
    """Validates that attacks are realistic"""

    def execute_task(self):
        # Read proposed attacks from ecosystem
        attacks = self.ecosystem.knowledge_base.get("attacks")

        # Challenge each attack
        validated = []
        rejected = []

        for attack in attacks:
            # Check 1: Is it valid SQL after decoding?
            decoded = self.decode_payload(attack['payload'])
            if not self.is_valid_sql(decoded):
                rejected.append({
                    'payload': attack['payload'],
                    'reason': 'Invalid SQL syntax',
                    'decoded': decoded
                })
                continue

            # Check 2: Would it actually exploit a vulnerability?
            if not self.can_exploit(decoded):
                rejected.append({
                    'payload': attack['payload'],
                    'reason': 'Does not exploit vulnerability',
                    'decoded': decoded
                })
                continue

            # Check 3: Is it realistic for an attacker?
            if not self.is_realistic(attack['payload']):
                rejected.append({
                    'payload': attack['payload'],
                    'reason': 'Unrealistic attack pattern',
                    'decoded': decoded
                })
                continue

            # Passed all checks
            validated.append(attack)

        return validated, rejected

# Agent #8 results:
validated_attacks = [
    {'payload': "admin' --", 'reason': 'Valid comment-based injection'},
    {'payload': "admin%27%20--", 'reason': 'Valid URL-encoded injection'},
]

rejected_attacks = [
    {
        'payload': "admin%27%20%5c%78%32%64%5c%78%32%64",
        'reason': 'Unrealistic - double-escaped hex in URL encoding',
        'feedback': 'Real attacker would not double-escape'
    }
]
```

**Red vs Blue Game**:
- **Red Team (Attackers)** try to generate evasions
- **Blue Team (Validators)** challenge unrealistic ones
- **Nash Equilibrium** reached at ~90% validation rate

---

### Stage 5: Testing Against Purple Agent

**Now test all validated attacks**

```python
# Test validated attacks
test_results = []

for attack in validated_attacks:
    result = purple_agent.detect(attack['payload'])

    test_results.append({
        'payload': attack['payload'],
        'ground_truth': True,  # It IS an injection
        'detected': result.detected,
        'is_FN': not result.detected  # False Negative if missed
    })

# Results from Round 1:
test_results = [
    {'payload': "admin' --", 'detected': False, 'is_FN': True},  # MISSED!
    {'payload': "admin%27%20--", 'detected': False, 'is_FN': True},  # MISSED!
    {'payload': "' OR '1'='1", 'detected': True, 'is_FN': False},  # Caught
]

# Calculate metrics by category
metrics = {
    'classic_sqli': {'F1': 0.95, 'TP': 18, 'FN': 2},
    'union_based': {'F1': 0.88, 'TP': 22, 'FN': 3},
    'blind_sqli': {'F1': 0.42, 'TP': 8, 'FN': 12},  # WEAK!
    'time_based': {'F1': 0.51, 'TP': 10, 'FN': 10},  # WEAK!
}
```

**Key Finding**: Purple Agent is **weak at blind SQL injection** (F1 = 0.42)

---

### Stage 6: Multi-Perspective Assessment (Perspective Agents)

**What they do**: Evaluate results from different viewpoints

**Example: 3 Perspective Agents**

```python
class PerspectiveAgent:
    """Evaluates from specific viewpoint"""

    def execute_task(self):
        results = self.ecosystem.knowledge_base.get("test_results")

        if self.perspective == "security_expert":
            return self.security_expert_view(results)
        elif self.perspective == "developer":
            return self.developer_view(results)
        elif self.perspective == "pentester":
            return self.pentester_view(results)

# Perspective 1: Security Expert
security_expert_assessment = {
    'severity': 'HIGH',
    'reasoning': 'Blind SQL injection weakness is critical - allows data exfiltration without error messages',
    'risk_score': 8.5,
    'recommendations': [
        'Add time-based detection (monitor response delays)',
        'Implement boolean-based blind detection',
        'Add comment syntax normalization'
    ]
}

# Perspective 2: Developer
developer_assessment = {
    'severity': 'MEDIUM',
    'reasoning': 'Detection rate is 88% overall, acceptable for initial release',
    'risk_score': 6.0,
    'recommendations': [
        'Focus on high-traffic endpoints first',
        'Add more test coverage for edge cases',
        'Consider parametrized queries'
    ]
}

# Perspective 3: Penetration Tester
pentester_assessment = {
    'severity': 'HIGH',
    'reasoning': 'Multiple exploitable bypasses found, attacker would find these quickly',
    'risk_score': 8.0,
    'recommendations': [
        'Test with real-world attack tools (sqlmap, etc.)',
        'Add WAF rule for comment-based evasions',
        'Implement multi-layer defense'
    ]
}
```

**Perspectives diverge**: Security Expert says HIGH, Developer says MEDIUM

---

### Stage 7: Debate & Consensus (LLMJudge Agents with Dawid-Skene)

**What they do**: Debate the severity, reach calibrated consensus

**Example: LLM Judge Panel Debate**

```python
class LLMJudgeAgent:
    """LLM-powered judge with debate capability"""

    def execute_task(self):
        # Each judge rates severity independently
        perspectives = self.ecosystem.knowledge_base.get("perspectives")

        # Judge 1 (Claude): Rates severity
        claude_rating = self.llm_evaluate(
            perspectives=perspectives,
            model="claude-3.5-sonnet"
        )

        # Judge 2 (GPT-4): Rates severity
        gpt4_rating = self.llm_evaluate(
            perspectives=perspectives,
            model="gpt-4"
        )

        # Judge 3 (Gemini): Rates severity
        gemini_rating = self.llm_evaluate(
            perspectives=perspectives,
            model="gemini-pro"
        )

        return {
            'claude': claude_rating,
            'gpt4': gpt4_rating,
            'gemini': gemini_rating
        }

# Individual judge ratings (1-5 scale)
judge_ratings = {
    'claude': 4,   # HIGH severity
    'gpt4': 4,     # HIGH severity
    'gemini': 3,   # MEDIUM-HIGH severity
}

# Apply Dawid-Skene calibration
calibrated_panel = CalibratedJudgePanel(judges=[claude, gpt4, gemini])

calibrated_result = calibrated_panel.evaluate_with_consensus(
    item=perspectives
)

# Calibrated consensus result:
consensus = {
    'mean_severity': 3.8,  # Between HIGH and MEDIUM-HIGH
    'credible_interval': (3.5, 4.1),  # Narrow CI = high confidence
    'uncertainty': 0.42,  # Low uncertainty
    'needs_arbitration': False,  # CI is narrow, no overlap
    'final_rating': 4,  # HIGH severity
    'confidence': 'HIGH'
}
```

**Consensus**: HIGH severity (rating 4), high confidence (narrow CI)

---

### Stage 8: Counterfactual Analysis (After detecting failures)

**What they do**: For each False Negative, find minimal fix

**Example: Counterfactual Analyzer**

```python
class CounterfactualAnalyzer:
    """Finds minimal edits to flip Purple Agent decision"""

    def analyze_failure(self, payload, ground_truth):
        # Failure: "admin' --" was not detected (FN)

        # Search for minimal change that WOULD be detected
        candidates = [
            # Add keyword
            "admin' OR --",
            "admin' UNION --",
            "admin' SELECT --",

            # Remove encoding
            "admin' --",  # Already decoded

            # Change structure
            "admin' OR 1=1 --",
        ]

        # Test each candidate
        for candidate in candidates:
            result = self.purple_agent.detect(candidate)
            if result.detected:
                # Found counterfactual!
                return {
                    'original': "admin' --",
                    'counterfactual': candidate,
                    'edit_distance': levenshtein("admin' --", candidate),
                    'patch_hint': self.generate_patch_hint(
                        "admin' --",
                        candidate
                    )
                }

        return None

# Counterfactual result:
counterfactual = {
    'original': "admin' --",
    'counterfactual': "admin' OR 1=1 --",
    'edit_distance': 9,  # Added "OR 1=1 "
    'patch_hint': "Add detection for comment syntax even without SQL keywords. Current rule requires keywords (OR, UNION, etc.) before detecting comments.",
    'actionable_fix': [
        'Rule: Detect single-quote followed by comment syntax',
        'Pattern: /\'[\\s]*--/',
        'Normalize whitespace before matching'
    ]
}
```

**Key Output**: Concrete fix for Purple Agent developers!

---

## 🎯 Round 1 Summary

After Round 1, the ecosystem has:

```
┌─────────────────────────────────────────────────────────────────┐
│                    Round 1 Results                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Tests Run: 50 attacks                                          │
│  Validated: 45 attacks (90% validation rate)                    │
│  Rejected: 5 attacks (unrealistic)                              │
│                                                                  │
│  Detection Metrics:                                             │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Overall F1:        0.71                                   │  │
│  │ Precision:         0.92                                   │  │
│  │ Recall:            0.58                                   │  │
│  │ False Negatives:   21 (missed attacks)                    │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  Per-Category F1:                                               │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ classic_sqli:      0.95  ✓ Strong                         │  │
│  │ union_based:       0.88  ✓ Good                           │  │
│  │ blind_sqli:        0.42  ⚠️ WEAK (identified!)            │  │
│  │ time_based:        0.51  ⚠️ WEAK                          │  │
│  │ comment_evasion:   0.38  ⚠️ WEAK                          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  Consensus Assessment:                                          │
│  • Severity: HIGH (4/5)                                         │
│  • Confidence: HIGH (CI: 3.5-4.1)                              │
│  • Key Weakness: Blind SQL injection                           │
│                                                                  │
│  Actionable Fixes: 3 counterfactual patch hints generated      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Round 2-10: ADAPTIVE EXPLOITATION

### Thompson Sampling Allocation

**What happens**: Orchestrator uses Bayesian optimization to focus on weak areas

```python
class ThompsonSamplingAllocator:
    """Bayesian test allocation"""

    def allocate_round_2(self):
        # Update posteriors based on Round 1 results

        # Context: (blind_sqli, encoding_mutator, boundary_bin_3)
        # Round 1: Found 12 evasions (successes)
        self.posteriors[('blind_sqli', 'encoding', 3)] = {
            'alpha': 1 + 12,  # Prior + successes
            'beta': 1 + 3      # Prior + failures
        }
        # Expected success rate: 13/17 = 0.76 (HIGH!)

        # Context: (classic_sqli, obfuscation_mutator, boundary_bin_5)
        # Round 1: Found 1 evasion
        self.posteriors[('classic_sqli', 'obfuscation', 5)] = {
            'alpha': 1 + 1,
            'beta': 1 + 14
        }
        # Expected success rate: 2/17 = 0.12 (LOW)

        # Sample from posteriors to allocate next 50 tests
        allocations = []
        for _ in range(50):
            max_sample = -1
            best_context = None

            for context, params in self.posteriors.items():
                # Sample from Beta(α, β)
                sample = beta.rvs(params['alpha'], params['beta'])

                if sample > max_sample:
                    max_sample = sample
                    best_context = context

            allocations.append(best_context)

        return allocations

# Round 2 allocation:
round_2_allocation = {
    'blind_sqli': 35 tests,      # 70% to weak area (was 60% heuristic)
    'time_based': 10 tests,      # 20%
    'classic_sqli': 5 tests      # 10% maintenance
}
```

**Result**: Focus shifts automatically to `blind_sqli` (highest expected yield)

---

### Coverage-Debt Tracking

**What happens**: Track systematic coverage of SQL injection techniques

```python
class CoverageDebtTracker:
    """Tracks coverage debt across MITRE-style taxonomy"""

    def calculate_debt(self):
        # SQL Injection Taxonomy:
        taxonomy = {
            'classic_sqli': {
                'target_coverage': 0.95,
                'achieved_coverage': 0.95,
                'debt': 0.0  # No debt
            },
            'union_based': {
                'target_coverage': 0.90,
                'achieved_coverage': 0.88,
                'debt': 0.02  # Small debt
            },
            'blind_sqli': {
                'target_coverage': 0.90,
                'achieved_coverage': 0.42,
                'debt': 0.48  # HIGH DEBT!
            },
            'time_based': {
                'target_coverage': 0.85,
                'achieved_coverage': 0.51,
                'debt': 0.34  # HIGH DEBT!
            },
            'error_based': {
                'target_coverage': 0.85,
                'achieved_coverage': 0.0,
                'debt': 0.85  # UNTESTED!
            }
        }

        # Add exploration bonus to high-debt areas
        return taxonomy

# Round 2-3: Focus on blind_sqli (highest debt)
# Round 4-5: Move to error_based (untested)
# Round 6-10: Refine all areas to target coverage
```

---

### Performance Improvement Over Rounds

```
Round 1:  blind_sqli F1 = 0.42  ⚠️
Round 2:  blind_sqli F1 = 0.55  (focused 35 tests)
Round 3:  blind_sqli F1 = 0.63  (focused 32 tests)
Round 4:  blind_sqli F1 = 0.71  (focused 28 tests)
Round 5:  blind_sqli F1 = 0.75  (focused 20 tests)
...
Round 10: blind_sqli F1 = 0.82  ✓ Converged

Convergence detected! (3 rounds with ΔF1 < 0.03)
```

**Thompson Sampling Impact**: Reached F1=0.82 in 10 rounds instead of 15-20 with heuristic allocation (25-40% faster)

---

## 📊 Final Evaluation Report

After 10 rounds, the ecosystem produces:

```
┌─────────────────────────────────────────────────────────────────┐
│         Final Evaluation Report: MySQLInjectionDetector          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  OVERALL METRICS                                                │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ F1 Score:           0.83  ✓                               │  │
│  │ Precision:          0.89  ✓                               │  │
│  │ Recall:             0.78  ✓                               │  │
│  │ Accuracy:           0.85  ✓                               │  │
│  │ False Positive Rate: 0.05 ✓                               │  │
│  │ False Negative Rate: 0.22 ⚠️                              │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  PER-CATEGORY PERFORMANCE                                       │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ classic_sqli:    F1=0.95  ████████████ Strong             │  │
│  │ union_based:     F1=0.88  ██████████░░ Good               │  │
│  │ blind_sqli:      F1=0.82  █████████░░░ Acceptable         │  │
│  │ time_based:      F1=0.79  ████████░░░░ Acceptable         │  │
│  │ error_based:     F1=0.74  ███████░░░░░ Needs work         │  │
│  │ nosql_injection: F1=0.68  ██████░░░░░░ Needs work         │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ROBUSTNESS (from Mutation Engine)                             │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Evasion Attempts:   250                                   │  │
│  │ Successful Evasions: 48 (19.2%)                           │  │
│  │ Robustness Score:   80.8% ✓                               │  │
│  │                                                           │  │
│  │ By Mutation Type:                                         │  │
│  │ • URL Encoding:      72% resistant ✓                      │  │
│  │ • Hex Encoding:      68% resistant ⚠️                     │  │
│  │ • Obfuscation:       55% resistant ⚠️ Weak!               │  │
│  │ • Structure Change:  85% resistant ✓                      │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  QUALITY ASSESSMENT (from Judge Panel)                          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Technical Correctness:  4.2/5  ████████░░                 │  │
│  │ Clarity of Detection:   3.8/5  ███████░░░                 │  │
│  │ Actionability:          4.5/5  █████████░                 │  │
│  │ Completeness:           3.9/5  ███████░░░                 │  │
│  │                                                           │  │
│  │ Calibrated Consensus: 4.1/5 (CI: 3.8-4.4) ✓ High conf    │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  DISCOVERED EVASION PATTERNS (Novel)                            │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ 1. Comment syntax with leading whitespace                │  │
│  │    Pattern: /'[\s]+--/                                    │  │
│  │    Example: admin' --                                     │  │
│  │                                                           │  │
│  │ 2. Mixed encoding (URL + Hex)                            │  │
│  │    Pattern: %XX followed by \xYY                         │  │
│  │    Example: admin%27%20\x2d\x2d                          │  │
│  │                                                           │  │
│  │ 3. Boolean blind with string comparison                  │  │
│  │    Pattern: ' OR 'a'='a                                  │  │
│  │    Example: 1' OR 'x'='x'--                              │  │
│  │                                                           │  │
│  │ 4. Time-based with BENCHMARK obfuscation                 │  │
│  │    Pattern: BENCHMARK(5000000,MD5('x'))                  │  │
│  │    Example: ' AND BENCHMARK(...)--                        │  │
│  │                                                           │  │
│  │ 5. Case variation in keywords                            │  │
│  │    Pattern: SeLeCt, UnIoN, etc.                          │  │
│  │    Example: ' uNiOn sElEcT password--                    │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ACTIONABLE REMEDIATION (Counterfactual Analysis)               │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Top 3 Recommended Fixes:                                 │  │
│  │                                                           │  │
│  │ 1. Normalize whitespace before comment detection (48%)   │  │
│  │    Fix: Strip/collapse whitespace before matching        │  │
│  │    Pattern: /\s+/ → ' '                                  │  │
│  │    Impact: Would catch 12 missed evasions                │  │
│  │                                                           │  │
│  │ 2. Add nested encoding detection (35%)                   │  │
│  │    Fix: Decode iteratively until stable                  │  │
│  │    Algorithm: while (decoded != prev) { decode() }       │  │
│  │    Impact: Would catch 9 missed evasions                 │  │
│  │                                                           │  │
│  │ 3. Implement case-insensitive keyword matching (17%)     │  │
│  │    Fix: .lower() before pattern match                    │  │
│  │    Pattern: /union/i instead of /UNION/                  │  │
│  │    Impact: Would catch 4 missed evasions                 │  │
│  │                                                           │  │
│  │ Combined Impact: 25 of 48 evasions (52%) would be caught │  │
│  │ New Estimated F1: 0.83 → 0.91 (+0.08)                    │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  COST STATISTICS                                                │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Total LLM API Calls:    125                              │  │
│  │ • Claude (expensive):    15 calls  ($3.75)               │  │
│  │ • GPT-4 (expensive):     15 calls  ($3.00)               │  │
│  │ • Gemini (cheap):        45 calls  ($0.90)               │  │
│  │ • GPT-3.5 (cheap):       50 calls  ($0.25)               │  │
│  │                                                           │  │
│  │ Total Cost: $7.90                                         │  │
│  │ Cost per Test: $0.16                                      │  │
│  │                                                           │  │
│  │ Without Cost Routing: ~$15.00 (saved 47%)  ✓             │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  REPRODUCIBILITY                                                │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ eBOM (Evaluation Bill of Materials):                     │  │
│  │ • Dataset version:     sql_injection_v2.3                │  │
│  │ • Prompt version:      prompts_v1.2                      │  │
│  │ • Model configs:       configs_20250107.json             │  │
│  │ • Random seed:         42                                │  │
│  │ • Framework version:   2.1.0                             │  │
│  │                                                           │  │
│  │ Signed Hash: sha256:8f3a9c2e...                          │  │
│  │ Reproducibility: 99.2% (re-run matched within tolerance) │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  EXECUTION STATISTICS                                           │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Total Rounds:           10                                │  │
│  │ Total Tests:           500                                │  │
│  │ Validated Attacks:     455 (91%)                          │  │
│  │ Rejected (Unrealistic): 45 (9%)                           │  │
│  │ Unique Evasion Families: 24 (2.4× baseline)              │  │
│  │ Arbitrations:          12 (2.4% of evaluations)           │  │
│  │ Convergence Round:      8                                 │  │
│  │ Safety Violations:      0 ✓                               │  │
│  │ Execution Time:        2.3 hours                          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🎯 Summary: How Each Agent Family Works

### 1. **BoundaryProber Agents** (5 agents)
- **Job**: Find decision boundaries
- **How**: Test diverse samples, identify where Purple Agent switches decisions
- **Output**: Boundary map (safe zones, vulnerable zones, unclear regions)
- **Example**: Discovered comment syntax boundary

### 2. **Exploiter Agents** (15 agents)
- **Job**: Generate attacks near boundaries (hardest to detect)
- **How**: Read boundaries, create variations in boundary regions
- **Output**: Candidate attacks with high evasion potential
- **Example**: Generated `admin' --` variations

### 3. **Mutator Agents** (25 agents: 10 encoding, 10 obfuscation, 5 structure)
- **Job**: Evolve attacks over generations
- **How**: Apply mutations, select by Pareto front (evasion × novelty)
- **Output**: Diverse attack families across generations
- **Example**: Found mixed encoding evasions
- **Enhancement**: Novelty search prevents mode collapse

### 4. **Validator Agents** (20 agents: 10 syntax, 10 semantic)
- **Job**: Ensure attacks are realistic
- **How**: Challenge unrealistic attacks, check syntax/semantics
- **Output**: Validated attacks only (reject ~10%)
- **Example**: Rejected double-escaped hex
- **Game**: Red vs Blue reaches Nash Equilibrium at ~90%

### 5. **Specialist Agents** (20 agents, per technique)
- **Job**: Deep expertise in specific SQL injection types
- **How**: Focus on one technique (blind, union, time-based, etc.)
- **Output**: Technique-specific evasions
- **Example**: Blind SQL specialist found boolean-based evasions

### 6. **Perspective Agents** (10 agents: security, dev, pentester)
- **Job**: Evaluate from different viewpoints
- **How**: Apply domain expertise to interpret results
- **Output**: Risk assessment from each perspective
- **Example**: Security Expert rated HIGH, Developer MEDIUM

### 7. **LLMJudge Agents** (5 agents: Claude, GPT-4, Gemini, etc.)
- **Job**: Provide quality assessment with debate
- **How**: LLM evaluates perspectives, debates with other judges
- **Output**: Calibrated consensus with confidence intervals
- **Example**: Consensus = 4.1/5 (CI: 3.8-4.4)
- **Enhancement**: Dawid-Skene models judge reliability

### 8. **Meta-Orchestrator** (1, coordinates everything)
- **Job**: Allocate tests, manage coalitions, detect convergence
- **How**: Thompson Sampling allocates based on posteriors
- **Output**: Test allocation strategy per round
- **Example**: Allocated 70% to blind_sqli in Round 2
- **Enhancement**: Bayesian optimization replaces heuristics

---

## 🔑 Key Takeaways

**Emergent Behavior:**
- No central script dictates "now do probing, then exploitation"
- Agents self-organize into coalitions based on shared goals
- Mechanisms (probing, exploitation, mutation, etc.) emerge from agent interactions

**Adaptive Intelligence:**
- Thompson Sampling automatically focuses on weak areas (blind_sqli)
- Novelty Search discovers 24 unique evasion families (vs 8 without)
- Coverage-Debt ensures systematic exploration (MITRE taxonomy)

**Production-Ready:**
- Sandbox prevents malicious code execution (0 safety violations)
- Cost optimization saves 47% on LLM calls
- Counterfactual analysis provides actionable fixes (52% of missed attacks fixable with 3 changes)
- eBOM enables 99.2% reproducibility

**Real Impact:**
- Found 48 evasions in production detector
- Identified 5 novel attack patterns
- Provided concrete remediation (not just "it's broken")
- Converged in 10 rounds (25-40% faster than heuristic)

---

This is how the Enhanced Unified Framework works in practice! 🚀
