# Framework Scenarios
**Centralized Repository for All Security Evaluation Scenarios**

---

## Overview

This is the **CENTRALIZED location for ALL security scenarios** in the evaluation framework.

All scenarios implement the `SecurityScenario` interface and work with the unified multi-agent evaluation system.

---

## Current Scenarios

### 1. SQL Injection (`sql_injection.py`)
**Status:** ✅ Complete
**Techniques:** Classic, Blind, Union-based, Time-based, Error-based
**Mutators:** Encoding, Obfuscation, Comment Injection, Case Variation
**Validators:** Syntax, Semantic, Realism

```python
from framework.scenarios import SQLInjectionScenario
scenario = SQLInjectionScenario()
```

### 2. Prompt Injection (`prompt_injection.py`)
**Status:** ✅ Complete
**Techniques:** Jailbreak, Prompt Leaking, Role Manipulation, Instruction Override, Resource Abuse, Data Exfiltration, Delimiter Attacks
**Mutators:** Encoding, Obfuscation, Template variations
**Validators:** LLM-specific validation

```python
from framework.scenarios import PromptInjectionScenario
scenario = PromptInjectionScenario()
```

---

## Planned Structure (100+ Scenarios)

```
framework/scenarios/
│
├── __init__.py
├── README.md                          ← This file
│
├── Current Scenarios
├── sql_injection.py                   ← SQL Injection (complete)
├── prompt_injection.py                ← Prompt Injection (complete)
│
├── Web Application Attacks (Phase 1: 6 scenarios)
├── web_attacks/
│   ├── __init__.py
│   ├── xss.py                         ← Cross-Site Scripting
│   ├── csrf.py                        ← Cross-Site Request Forgery
│   ├── command_injection.py           ← OS Command Injection
│   ├── path_traversal.py              ← Path Traversal
│   ├── xxe.py                         ← XML External Entity
│   └── deserialization.py             ← Deserialization Attacks
│
├── Network Attacks (Phase 2: 3 scenarios)
├── network_attacks/
│   ├── __init__.py
│   ├── ddos.py                        ← DDoS Detection
│   ├── port_scanning.py               ← Port Scanning
│   └── dns_tunneling.py               ← DNS Tunneling
│
├── Social Engineering (Phase 3: 2 scenarios)
├── social_engineering/
│   ├── __init__.py
│   ├── phishing.py                    ← Email Phishing
│   └── smishing.py                    ← SMS Phishing
│
└── MITRE ATT&CK (Phase 4: 50+ scenarios)
    └── mitre/
        ├── __init__.py
        ├── initial_access/
        │   ├── __init__.py
        │   ├── t1190_exploit_public_facing.py
        │   ├── t1566_phishing.py
        │   └── ...
        ├── execution/
        │   ├── __init__.py
        │   ├── t1059_command_scripting.py
        │   └── ...
        ├── persistence/
        │   ├── __init__.py
        │   ├── t1078_valid_accounts.py
        │   └── ...
        ├── privilege_escalation/
        ├── defense_evasion/
        ├── credential_access/
        ├── discovery/
        ├── lateral_movement/
        ├── collection/
        ├── exfiltration/
        ├── command_and_control/
        └── impact/
```

---

## Adding a New Scenario

### Step 1: Create the Scenario File (30 minutes)

```python
# framework/scenarios/web_attacks/xss.py

from typing import List
from framework.base import SecurityScenario, Mutator, Validator
from framework.models import Attack, AttackCategory

class XSSScenario(SecurityScenario):
    """Cross-Site Scripting scenario."""

    def __init__(self):
        super().__init__(
            name="XSS Detection",
            description="Evaluates XSS detection capabilities",
            attack_types=["reflected", "stored", "dom_based", "mutation"]
        )

    def get_mutators(self) -> List[Mutator]:
        """Return XSS-specific mutators."""
        return [
            EncodingMutator(['html_entity', 'url', 'unicode']),
            ObfuscationMutator(['case_variation', 'string_concat']),
            ContextMutator(['attribute', 'script', 'style'])
        ]

    def get_validators(self) -> List[Validator]:
        """Return XSS-specific validators."""
        return [
            SyntaxValidator(),
            SemanticValidator(),
            RealismValidator()
        ]
```

### Step 2: Implement Mutators (1-2 hours)

```python
class EncodingMutator(Mutator):
    """XSS encoding mutations."""

    def mutate(self, attack: Attack) -> List[Attack]:
        mutations = []
        payload = attack.payload

        # HTML entity encoding
        html_encoded = self.html_encode(payload)
        mutations.append(self._create_mutation(attack, html_encoded, 'html_entity'))

        # URL encoding
        url_encoded = urllib.parse.quote(payload)
        mutations.append(self._create_mutation(attack, url_encoded, 'url'))

        return mutations
```

### Step 3: Register the Scenario (5 minutes)

```python
# framework/scenarios/__init__.py

from .web_attacks.xss import XSSScenario

__all__ = [
    'SQLInjectionScenario',
    'PromptInjectionScenario',
    'XSSScenario',  # ← Add here
]
```

### Step 4: Use It (instant)

```python
from framework import create_ecosystem
from framework.scenarios import XSSScenario

scenario = XSSScenario()
ecosystem = create_ecosystem(scenario, llm_mode='cheap')
result = ecosystem.evaluate(purple_agent, max_rounds=10)
```

**Total Time:** 4-6 hours for a complete scenario

---

## Scenario Interface

All scenarios must implement the `SecurityScenario` interface:

```python
from abc import ABC, abstractmethod
from framework.base import SecurityScenario

class YourScenario(SecurityScenario):
    """Your scenario description."""

    def __init__(self):
        super().__init__(
            name="Scenario Name",
            description="What this scenario tests",
            attack_types=["type1", "type2"]
        )

    def get_mutators(self) -> List[Mutator]:
        """Return mutation operators."""
        raise NotImplementedError

    def get_validators(self) -> List[Validator]:
        """Return validation rules."""
        raise NotImplementedError

    def get_dataset(self) -> Dataset:
        """Return test dataset (optional)."""
        return Dataset.load(f'datasets/{self.name}')
```

---

## MITRE ATT&CK Integration

### Naming Convention

MITRE scenarios follow this pattern:

```
framework/scenarios/mitre/{tactic}/t{id}_{name}.py

Example:
framework/scenarios/mitre/initial_access/t1190_exploit_public_facing.py
```

### MITRE Scenario Template

```python
# framework/scenarios/mitre/initial_access/t1190_exploit_public_facing.py

from framework.base import SecurityScenario

class T1190ExploitPublicFacingScenario(SecurityScenario):
    """
    MITRE ATT&CK T1190: Exploit Public-Facing Application

    Tactic: Initial Access
    Technique: Exploit Public-Facing Application
    """

    def __init__(self):
        super().__init__(
            name="T1190 - Exploit Public-Facing Application",
            description=(
                "Evaluates detection of exploitation attempts against "
                "public-facing web servers, application servers, and databases."
            ),
            attack_types=["sql_injection", "rce", "file_upload", "xxe"],
            mitre_id="T1190",
            mitre_tactic="Initial Access"
        )
```

### Generating MITRE Scenarios

For 200+ MITRE techniques, use the scenario generator:

```python
# framework/tools/mitre_generator.py

from framework.mitre import MITREScenarioGenerator

generator = MITREScenarioGenerator()

# Generate scenario for specific technique
scenario_code = generator.generate_scenario("T1190")

# Generate all scenarios for a tactic
scenarios = generator.generate_tactic("Initial Access")

# Generate all scenarios (200+)
all_scenarios = generator.generate_all()
```

---

## Directory Organization

### Current (2 scenarios)
```
framework/scenarios/
├── sql_injection.py
└── prompt_injection.py
```

### Phase 1 (8 scenarios) - Web Attacks
```
framework/scenarios/
├── sql_injection.py
├── prompt_injection.py
└── web_attacks/
    ├── xss.py
    ├── csrf.py
    ├── command_injection.py
    ├── path_traversal.py
    ├── xxe.py
    └── deserialization.py
```

### Phase 2 (11 scenarios) - Add Network
```
framework/scenarios/
├── ...
├── web_attacks/
└── network_attacks/
    ├── ddos.py
    ├── port_scanning.py
    └── dns_tunneling.py
```

### Phase 3 (13 scenarios) - Add Social Engineering
```
framework/scenarios/
├── ...
├── network_attacks/
└── social_engineering/
    ├── phishing.py
    └── smishing.py
```

### Phase 4 (60+ scenarios) - MITRE ATT&CK
```
framework/scenarios/
├── ...
├── social_engineering/
└── mitre/
    ├── initial_access/ (5 scenarios)
    ├── execution/ (8 scenarios)
    ├── persistence/ (8 scenarios)
    ├── privilege_escalation/ (6 scenarios)
    ├── defense_evasion/ (10 scenarios)
    ├── credential_access/ (8 scenarios)
    ├── discovery/ (5 scenarios)
    ├── lateral_movement/ (6 scenarios)
    ├── collection/ (5 scenarios)
    ├── exfiltration/ (4 scenarios)
    ├── command_and_control/ (6 scenarios)
    └── impact/ (3 scenarios)
```

---

## Best Practices

### 1. Follow the Interface
- Always extend `SecurityScenario`
- Implement all required methods
- Return proper types

### 2. Provide Complete Implementations
- Include mutators (3-7 types)
- Include validators (2-4 types)
- Include dataset (50+ examples)

### 3. Document Thoroughly
- Clear docstrings
- Example usage
- MITRE mapping (if applicable)

### 4. Test Before Committing
```bash
# Test your scenario
pytest tests/test_your_scenario.py -v

# Run example evaluation
python framework/examples/test_your_scenario.py
```

### 5. Register in __init__.py
```python
# framework/scenarios/__init__.py
from .your_scenario import YourScenario

__all__ = [..., 'YourScenario']
```

---

## Related Documentation

- **[/framework/docs/FUTURE_IMPROVEMENTS.md](../docs/FUTURE_IMPROVEMENTS.md)** - Detailed scenario addition guide
- **[/framework/docs/SCALABILITY_GUIDE.md](../docs/SCALABILITY_GUIDE.md)** - Multi-attack scalability
- **[/framework/docs/ARCHITECTURE_GUIDE.md](../docs/ARCHITECTURE_GUIDE.md)** - System architecture

---

## Roadmap

| Phase | Scenarios | Timeline | Status |
|-------|-----------|----------|--------|
| Phase 0 | SQL Injection, Prompt Injection | Complete | ✅ Done |
| Phase 1 | 6 Web Attacks | 6 weeks | 📝 Planned |
| Phase 2 | 3 Network Attacks | 4 weeks | 📝 Planned |
| Phase 3 | 2 Social Engineering | 3 weeks | 📝 Planned |
| Phase 4 | 50+ MITRE Techniques | 6 months | 📝 Planned |

**Total Target:** 60+ scenarios covering major attack vectors and MITRE ATT&CK

---

**This is the centralized location for all scenarios. Do not create scenarios elsewhere.**

**Version:** 3.0
**Last Updated:** 2025-11-09
