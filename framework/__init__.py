"""
Unified Adaptive Security Evaluation Framework

A unified agent-based framework for evaluating security mechanisms across
multiple attack types (SQL Injection, XSS, DDoS, etc.).

Key Features:
- Unified agent ecosystem (single architecture for all attack types)
- Capability-based agents with dynamic coalition formation
- Thompson Sampling for adaptive test allocation
- Diversity-preserving evolution with novelty search
- Calibrated judge consensus with Dawid-Skene model
- Counterfactual failure analysis
- Multi-perspective assessment
- Formal sandbox isolation
- Cost-aware orchestration
- MITRE ATT&CK coverage tracking
- Reproducibility with eBOM

Version: 2.1
Based on: UNIFIED_ARCHITECTURE.md and ENHANCED_DESIGN.md
"""

# Base abstractions
from .base import (
    SecurityScenario,
    Mutator,
    Validator,
    UnifiedAgent,
    PurpleAgent,
    Coalition,
    KnowledgeBase,
    Capability,
    AgentRole,
    CoalitionType,
    Phase,
    Task,
    KnowledgeEntry,
    CoalitionGoal,
    AgentCapabilities
)

# Data models
from .models import (
    Attack,
    TestResult,
    TestOutcome,
    EvaluationResult,
    Metrics,
    PerspectiveAssessment,
    CounterfactualResult,
    CoverageReport,
    BehaviorDescriptor,
    AttackStatus,
    Severity,
    create_attack_id,
    create_result_id,
    calculate_outcome
)

# Knowledge base
from .knowledge_base import (
    InMemoryKnowledgeBase,
    PersistentKnowledgeBase
)

# Agents
from .agents import (
    BoundaryProberAgent,
    ExploiterAgent,
    MutatorAgent,
    ValidatorAgent,
    PerspectiveAgent,
    LLMJudgeAgent,
    CounterfactualAgent
)

# Orchestration
from .orchestrator import (
    MetaOrchestrator,
    ThompsonSamplingAllocator
)

# Main ecosystem
from .ecosystem import (
    UnifiedEcosystem,
    create_ecosystem
)

__version__ = '2.1.0'

__all__ = [
    # Base abstractions
    'SecurityScenario',
    'Mutator',
    'Validator',
    'UnifiedAgent',
    'PurpleAgent',
    'Coalition',
    'KnowledgeBase',
    'Capability',
    'AgentRole',
    'CoalitionType',
    'Phase',
    'Task',
    'KnowledgeEntry',
    'CoalitionGoal',
    'AgentCapabilities',

    # Data models
    'Attack',
    'TestResult',
    'TestOutcome',
    'EvaluationResult',
    'Metrics',
    'PerspectiveAssessment',
    'CounterfactualResult',
    'CoverageReport',
    'BehaviorDescriptor',
    'AttackStatus',
    'Severity',
    'create_attack_id',
    'create_result_id',
    'calculate_outcome',

    # Knowledge base
    'InMemoryKnowledgeBase',
    'PersistentKnowledgeBase',

    # Agents
    'BoundaryProberAgent',
    'ExploiterAgent',
    'MutatorAgent',
    'ValidatorAgent',
    'PerspectiveAgent',
    'LLMJudgeAgent',
    'CounterfactualAgent',

    # Orchestration
    'MetaOrchestrator',
    'ThompsonSamplingAllocator',

    # Main ecosystem
    'UnifiedEcosystem',
    'create_ecosystem',
]
