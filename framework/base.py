"""
Core abstractions for the Unified Adaptive Security Evaluation Framework.

This module defines the foundational interfaces and base classes that all
components build upon. Based on UNIFIED_ARCHITECTURE.md v2.1.

Key Concepts:
- SecurityScenario: Abstract interface for security evaluation scenarios
- UnifiedAgent: Capability-based agent architecture
- Coalition: Dynamic team formation for collaborative testing
- Capability: Agent capabilities (PROBE, GENERATE, MUTATE, etc.)
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Set, Tuple, Callable
from datetime import datetime
import logging


# ============================================================================
# ENUMS
# ============================================================================

class Capability(Enum):
    """Agent capabilities in the unified framework."""
    PROBE = auto()      # Boundary learning and exploration
    GENERATE = auto()   # Attack generation and exploitation
    MUTATE = auto()     # Evolutionary optimization
    VALIDATE = auto()   # Result validation (syntax, semantic)
    EVALUATE = auto()   # Quality assessment and perspective
    DEBATE = auto()     # Multi-judge consensus and arbitration


class AgentRole(Enum):
    """Agent roles within coalitions."""
    BOUNDARY_PROBER = auto()
    EXPLOITER = auto()
    MUTATOR = auto()
    VALIDATOR = auto()
    PERSPECTIVE = auto()
    LLM_JUDGE = auto()
    COUNTERFACTUAL_ANALYZER = auto()
    META_ORCHESTRATOR = auto()


class CoalitionType(Enum):
    """Types of coalitions that can form."""
    ATTACKER = auto()        # Generate and optimize attacks
    VALIDATOR = auto()       # Validate and verify results
    DEBATE = auto()          # Consensus building
    EXPLORATION = auto()     # Boundary learning
    EXPLOITATION = auto()    # Targeted attack generation


class Phase(Enum):
    """Evaluation phases."""
    EXPLORATION = auto()     # Boundary learning
    EXPLOITATION = auto()    # Attack generation
    VALIDATION = auto()      # Red vs Blue validation
    CONSENSUS = auto()       # Multi-perspective assessment
    COMPLETE = auto()        # Evaluation finished


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class AgentCapabilities:
    """Defines what an agent can do."""
    capabilities: Set[Capability]
    role: AgentRole
    requires_llm: bool = False
    cost_per_invocation: float = 0.0
    avg_latency_ms: float = 0.0


@dataclass
class Task:
    """Represents a task to be executed by an agent or coalition."""
    task_id: str
    task_type: str
    description: str
    parameters: Dict[str, Any]
    priority: float = 0.5
    created_at: datetime = field(default_factory=datetime.now)
    assigned_to: Optional[str] = None  # Agent ID or Coalition ID
    status: str = "pending"  # pending, in_progress, completed, failed
    result: Optional[Any] = None


@dataclass
class KnowledgeEntry:
    """Entry in the shared knowledge base."""
    entry_id: str
    source_agent: str
    timestamp: datetime
    entry_type: str  # boundary, attack, result, insight, metric
    data: Dict[str, Any]
    confidence: float = 1.0
    tags: Set[str] = field(default_factory=set)


@dataclass
class CoalitionGoal:
    """Goal for a coalition to achieve."""
    goal_id: str
    goal_type: str
    description: str
    required_capabilities: Set[Capability]
    success_criteria: Dict[str, Any]
    deadline: Optional[datetime] = None


# ============================================================================
# ABSTRACT BASE CLASSES
# ============================================================================

class SecurityScenario(ABC):
    """
    Abstract base class for security evaluation scenarios.

    Each scenario (SQL Injection, XSS, DDoS, etc.) implements this interface
    to integrate with the unified framework.
    """

    @abstractmethod
    def get_name(self) -> str:
        """Return scenario name (e.g., 'sql_injection', 'xss')."""
        pass

    @abstractmethod
    def get_techniques(self) -> List[str]:
        """
        Return list of attack techniques for this scenario.

        Examples:
        - SQL Injection: ['union_based', 'blind_boolean', 'time_based']
        - XSS: ['reflected', 'stored', 'dom_based']
        """
        pass

    @abstractmethod
    def get_mutators(self) -> List['Mutator']:
        """
        Return list of mutation strategies for this scenario.

        Mutators transform attacks to evade detection.
        """
        pass

    @abstractmethod
    def get_validators(self) -> List['Validator']:
        """
        Return list of validators for this scenario.

        Validators check attack validity (syntax, semantics, realism).
        """
        pass

    @abstractmethod
    def create_attack(self, technique: str, payload: Any, metadata: Dict[str, Any]) -> 'Attack':
        """
        Create an attack instance for this scenario.

        Args:
            technique: Attack technique (from get_techniques())
            payload: Attack payload (type varies by scenario)
            metadata: Additional attack metadata

        Returns:
            Attack instance
        """
        pass

    @abstractmethod
    def execute_attack(self, attack: 'Attack', target: 'PurpleAgent') -> 'TestResult':
        """
        Execute an attack against a target agent.

        Args:
            attack: Attack to execute
            target: Purple agent to test

        Returns:
            Test result with detection outcome
        """
        pass

    def get_mitre_mapping(self) -> Dict[str, List[str]]:
        """
        Return MITRE ATT&CK technique mapping.

        Optional: Override to provide MITRE coverage tracking.

        Returns:
            Mapping of scenario techniques to MITRE technique IDs
        """
        return {}

    def get_baseline_dataset(self) -> Optional[List['Attack']]:
        """
        Return baseline attack dataset for this scenario.

        Optional: Override to provide known attack samples.
        """
        return None


class Mutator(ABC):
    """
    Abstract base class for mutation strategies.

    Mutators transform attacks to evade detection while maintaining validity.
    """

    @abstractmethod
    def mutate(self, attack: 'Attack') -> List['Attack']:
        """
        Generate mutations of an attack.

        Args:
            attack: Base attack to mutate

        Returns:
            List of mutated attacks (typically 3-10 variants)
        """
        pass

    @abstractmethod
    def get_mutation_type(self) -> str:
        """Return mutation type (e.g., 'encoding', 'obfuscation')."""
        pass

    def get_diversity_score(self, attack1: 'Attack', attack2: 'Attack') -> float:
        """
        Calculate diversity between two attacks.

        Used for novelty search. Override for scenario-specific diversity.

        Args:
            attack1, attack2: Attacks to compare

        Returns:
            Diversity score in [0, 1] where 1 = maximally diverse
        """
        return 0.5  # Default: medium diversity


class Validator(ABC):
    """
    Abstract base class for attack validators.

    Validators ensure attacks are valid before testing.
    """

    @abstractmethod
    def validate(self, attack: 'Attack') -> Tuple[bool, Optional[str]]:
        """
        Validate an attack.

        Args:
            attack: Attack to validate

        Returns:
            Tuple of (is_valid, error_message)
            - is_valid: True if attack is valid
            - error_message: None if valid, error description if invalid
        """
        pass

    @abstractmethod
    def get_validator_type(self) -> str:
        """Return validator type (e.g., 'syntax', 'semantic', 'realism')."""
        pass


# ============================================================================
# UNIFIED AGENT BASE CLASS
# ============================================================================

class UnifiedAgent(ABC):
    """
    Base class for all agents in the unified framework.

    Agents are capability-based and can join coalitions dynamically.
    """

    def __init__(
        self,
        agent_id: str,
        capabilities: AgentCapabilities,
        knowledge_base: 'KnowledgeBase'
    ):
        """
        Initialize agent.

        Args:
            agent_id: Unique agent identifier
            capabilities: Agent capabilities
            knowledge_base: Shared knowledge base
        """
        self.agent_id = agent_id
        self.capabilities = capabilities
        self.knowledge_base = knowledge_base
        self.logger = logging.getLogger(f"Agent.{agent_id}")

        # State
        self.current_coalition: Optional['Coalition'] = None
        self.task_history: List[Task] = []
        self.metrics: Dict[str, float] = {}

    @abstractmethod
    def execute_task(self, task: Task) -> Any:
        """
        Execute a task assigned to this agent.

        Args:
            task: Task to execute

        Returns:
            Task result (type varies by task)
        """
        pass

    def can_execute(self, task: Task) -> bool:
        """
        Check if agent can execute a task.

        Args:
            task: Task to check

        Returns:
            True if agent has required capabilities
        """
        # Default: Check if task type matches any capability
        return True  # Override in subclasses for specific logic

    def join_coalition(self, coalition: 'Coalition'):
        """Join a coalition."""
        self.current_coalition = coalition
        self.logger.info(f"Joined coalition {coalition.coalition_id}")

    def leave_coalition(self):
        """Leave current coalition."""
        if self.current_coalition:
            self.logger.info(f"Left coalition {self.current_coalition.coalition_id}")
            self.current_coalition = None

    def share_knowledge(self, entry_type: str, data: Dict[str, Any], tags: Set[str] = None):
        """
        Share knowledge with other agents via knowledge base.

        Args:
            entry_type: Type of knowledge (boundary, attack, result, etc.)
            data: Knowledge data
            tags: Optional tags for filtering
        """
        entry = KnowledgeEntry(
            entry_id=f"{self.agent_id}_{datetime.now().timestamp()}",
            source_agent=self.agent_id,
            timestamp=datetime.now(),
            entry_type=entry_type,
            data=data,
            tags=tags or set()
        )
        self.knowledge_base.add_entry(entry)

    def query_knowledge(self, entry_type: Optional[str] = None, tags: Optional[Set[str]] = None) -> List[KnowledgeEntry]:
        """
        Query knowledge base.

        Args:
            entry_type: Filter by entry type
            tags: Filter by tags

        Returns:
            List of matching knowledge entries
        """
        return self.knowledge_base.query(entry_type=entry_type, tags=tags)

    def get_role(self) -> AgentRole:
        """Get agent role."""
        return self.capabilities.role

    def requires_llm(self) -> bool:
        """Check if agent requires LLM."""
        return self.capabilities.requires_llm

    def update_metrics(self, metrics: Dict[str, float]):
        """Update agent metrics."""
        self.metrics.update(metrics)


# ============================================================================
# COALITION
# ============================================================================

class Coalition:
    """
    Dynamic coalition of agents working toward a shared goal.

    Coalitions form and dissolve based on goals and required capabilities.
    """

    def __init__(
        self,
        coalition_id: str,
        coalition_type: CoalitionType,
        goal: CoalitionGoal,
        knowledge_base: 'KnowledgeBase'
    ):
        """
        Initialize coalition.

        Args:
            coalition_id: Unique coalition identifier
            coalition_type: Type of coalition
            goal: Coalition goal
            knowledge_base: Shared knowledge base
        """
        self.coalition_id = coalition_id
        self.coalition_type = coalition_type
        self.goal = goal
        self.knowledge_base = knowledge_base
        self.logger = logging.getLogger(f"Coalition.{coalition_id}")

        # Members
        self.members: List[UnifiedAgent] = []
        self.member_roles: Dict[str, AgentRole] = {}  # agent_id -> role

        # State
        self.created_at = datetime.now()
        self.status = "active"  # active, completed, dissolved
        self.tasks: List[Task] = []
        self.results: List[Any] = []

    def add_member(self, agent: UnifiedAgent):
        """
        Add agent to coalition.

        Args:
            agent: Agent to add
        """
        self.members.append(agent)
        self.member_roles[agent.agent_id] = agent.get_role()
        agent.join_coalition(self)
        self.logger.info(f"Added agent {agent.agent_id} with role {agent.get_role()}")

    def remove_member(self, agent_id: str):
        """
        Remove agent from coalition.

        Args:
            agent_id: Agent to remove
        """
        self.members = [a for a in self.members if a.agent_id != agent_id]
        if agent_id in self.member_roles:
            del self.member_roles[agent_id]
        self.logger.info(f"Removed agent {agent_id}")

    def has_required_capabilities(self) -> bool:
        """
        Check if coalition has all required capabilities for goal.

        Returns:
            True if all required capabilities present
        """
        member_capabilities = set()
        for member in self.members:
            member_capabilities.update(member.capabilities.capabilities)

        return self.goal.required_capabilities.issubset(member_capabilities)

    def assign_task(self, task: Task) -> Optional[UnifiedAgent]:
        """
        Assign task to appropriate member.

        Args:
            task: Task to assign

        Returns:
            Agent assigned to task, or None if no suitable agent
        """
        for member in self.members:
            if member.can_execute(task):
                task.assigned_to = member.agent_id
                task.status = "assigned"
                self.tasks.append(task)
                self.logger.info(f"Assigned task {task.task_id} to {member.agent_id}")
                return member

        self.logger.warning(f"No agent can execute task {task.task_id}")
        return None

    def execute(self) -> List[Any]:
        """
        Execute coalition goal.

        Returns:
            List of results from coalition execution
        """
        self.logger.info(f"Executing goal: {self.goal.description}")

        # Check we have required capabilities
        if not self.has_required_capabilities():
            missing = self.goal.required_capabilities - set().union(
                *[m.capabilities.capabilities for m in self.members]
            )
            self.logger.error(f"Missing capabilities: {missing}")
            self.status = "failed"
            return []

        # Execute tasks
        results = []
        for task in self.tasks:
            if task.assigned_to:
                agent = next((a for a in self.members if a.agent_id == task.assigned_to), None)
                if agent:
                    task.status = "in_progress"
                    result = agent.execute_task(task)
                    task.status = "completed"
                    task.result = result
                    results.append(result)

        self.results = results
        self.status = "completed"
        return results

    def dissolve(self):
        """Dissolve coalition."""
        self.logger.info(f"Dissolving coalition")
        for member in self.members:
            member.leave_coalition()
        self.status = "dissolved"
        self.members.clear()


# ============================================================================
# KNOWLEDGE BASE INTERFACE
# ============================================================================

class KnowledgeBase(ABC):
    """
    Shared knowledge base for agent communication.

    Agents read and write knowledge entries to coordinate without
    direct communication.
    """

    @abstractmethod
    def add_entry(self, entry: KnowledgeEntry):
        """Add knowledge entry."""
        pass

    @abstractmethod
    def query(
        self,
        entry_type: Optional[str] = None,
        tags: Optional[Set[str]] = None,
        source_agent: Optional[str] = None,
        since: Optional[datetime] = None
    ) -> List[KnowledgeEntry]:
        """
        Query knowledge base.

        Args:
            entry_type: Filter by entry type
            tags: Filter by tags (returns entries with ANY matching tag)
            source_agent: Filter by source agent
            since: Filter by timestamp (entries after this time)

        Returns:
            List of matching entries
        """
        pass

    @abstractmethod
    def get_latest(self, entry_type: str, n: int = 10) -> List[KnowledgeEntry]:
        """
        Get latest N entries of a type.

        Args:
            entry_type: Entry type to query
            n: Number of entries to return

        Returns:
            Latest N entries, sorted by timestamp descending
        """
        pass

    @abstractmethod
    def clear(self):
        """Clear all knowledge (for testing or reset)."""
        pass


# ============================================================================
# PURPLE AGENT INTERFACE
# ============================================================================

class PurpleAgent(ABC):
    """
    Interface for purple agents (systems under test).

    Purple agents are the security mechanisms being evaluated.
    """

    @abstractmethod
    def detect(self, attack: 'Attack') -> 'TestResult':
        """
        Test if attack is detected.

        Args:
            attack: Attack to test

        Returns:
            Test result with detection outcome
        """
        pass

    @abstractmethod
    def get_name(self) -> str:
        """Return purple agent name."""
        pass

    @abstractmethod
    def reset(self):
        """Reset purple agent state (for stateful agents)."""
        pass


# ============================================================================
# PLACEHOLDER IMPORTS (defined in models.py)
# ============================================================================

# These are forward references - actual classes defined in models.py
# Kept here for type hints
Attack = Any
TestResult = Any
EvaluationResult = Any
