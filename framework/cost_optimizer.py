"""
Cost Optimizer - Smart model routing and budget enforcement.

Dynamically routes LLM requests to cheaper models when possible,
reserves expensive models for complex tasks.
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass
import logging

from .base import Task


@dataclass
class LLMModel:
    """LLM model with cost/performance characteristics."""
    name: str
    cost_per_1k_tokens: float
    avg_quality_score: float  # 0.0-1.0
    avg_latency_ms: float
    context_window: int


class ModelRouter:
    """
    Routes LLM requests to appropriate model based on task complexity.

    Strategy:
    - Simple tasks (e.g., syntax check) → Cheap model
    - Complex tasks (e.g., novel attack generation) → Expensive model
    - Automatically learns task complexity from outcomes
    """

    def __init__(self, models: List[LLMModel]):
        """
        Initialize model router.

        Args:
            models: Available LLM models, sorted by cost (cheap → expensive)
        """
        self.models = sorted(models, key=lambda m: m.cost_per_1k_tokens)
        self.logger = logging.getLogger("ModelRouter")

        # Task complexity tracking
        self.task_complexity: Dict[str, float] = {}  # task_type → complexity [0, 1]
        self.task_outcomes: Dict[str, List[float]] = {}  # task_type → quality scores

    def route(self, task: Task, prompt: str) -> LLMModel:
        """
        Route task to appropriate model.

        Args:
            task: Task to execute
            prompt: LLM prompt

        Returns:
            Selected LLM model
        """
        # Get task complexity (learned from history)
        complexity = self.task_complexity.get(task.task_type, 0.5)  # Default: medium

        # Calculate prompt complexity
        prompt_complexity = self._estimate_prompt_complexity(prompt)

        # Combined complexity
        total_complexity = 0.7 * complexity + 0.3 * prompt_complexity

        # Select model based on complexity
        if total_complexity < 0.3:
            # Simple task → cheapest model
            model = self.models[0]
        elif total_complexity < 0.7:
            # Medium task → mid-tier model
            model = self.models[len(self.models) // 2]
        else:
            # Complex task → expensive model
            model = self.models[-1]

        self.logger.info(f"Routing {task.task_type} (complexity={total_complexity:.2f}) to {model.name}")
        return model

    def update(self, task_type: str, quality_score: float):
        """
        Update task complexity based on outcome.

        Args:
            task_type: Type of task executed
            quality_score: Quality of result (0.0-1.0)
        """
        if task_type not in self.task_outcomes:
            self.task_outcomes[task_type] = []

        self.task_outcomes[task_type].append(quality_score)

        # Calculate average quality
        avg_quality = sum(self.task_outcomes[task_type]) / len(self.task_outcomes[task_type])

        # If quality is low, increase complexity (route to better model next time)
        if avg_quality < 0.6:
            self.task_complexity[task_type] = min(1.0, self.task_complexity.get(task_type, 0.5) + 0.1)
        # If quality is high with cheap model, complexity is low
        elif avg_quality > 0.8:
            self.task_complexity[task_type] = max(0.0, self.task_complexity.get(task_type, 0.5) - 0.1)

    def _estimate_prompt_complexity(self, prompt: str) -> float:
        """
        Estimate prompt complexity from content.

        Args:
            prompt: LLM prompt

        Returns:
            Complexity score [0, 1]
        """
        complexity_score = 0.0

        # Length-based complexity
        if len(prompt) > 2000:
            complexity_score += 0.3
        elif len(prompt) > 500:
            complexity_score += 0.15

        # Keyword-based complexity
        complex_keywords = ['analyze', 'compare', 'synthesize', 'evaluate', 'novel', 'creative']
        simple_keywords = ['check', 'validate', 'detect', 'classify']

        prompt_lower = prompt.lower()
        for keyword in complex_keywords:
            if keyword in prompt_lower:
                complexity_score += 0.1

        for keyword in simple_keywords:
            if keyword in prompt_lower:
                complexity_score -= 0.1

        return max(0.0, min(1.0, complexity_score))


class BudgetEnforcer:
    """
    Enforces cost budget during evaluation.

    Strategies:
    - Hard stop when budget exceeded
    - Soft limit with warnings
    - Budget allocation per phase
    """

    def __init__(self, total_budget_usd: float):
        """
        Initialize budget enforcer.

        Args:
            total_budget_usd: Total budget for evaluation
        """
        self.total_budget = total_budget_usd
        self.spent = 0.0
        self.logger = logging.getLogger("BudgetEnforcer")

        # Phase budgets (% of total)
        self.phase_budgets = {
            'exploration': 0.15,    # 15% for boundary probing
            'exploitation': 0.50,   # 50% for attack generation
            'validation': 0.20,     # 20% for validation
            'consensus': 0.15       # 15% for assessment
        }

        self.phase_spent = {phase: 0.0 for phase in self.phase_budgets}

    def can_afford(self, cost: float, phase: Optional[str] = None) -> bool:
        """
        Check if operation is within budget.

        Args:
            cost: Operation cost
            phase: Optional phase name

        Returns:
            True if within budget
        """
        # Check total budget
        if self.spent + cost > self.total_budget:
            self.logger.warning(f"Total budget exceeded: ${self.spent + cost:.2f} > ${self.total_budget:.2f}")
            return False

        # Check phase budget
        if phase:
            phase_budget = self.total_budget * self.phase_budgets.get(phase, 0.25)
            phase_spent = self.phase_spent.get(phase, 0.0)

            if phase_spent + cost > phase_budget:
                self.logger.warning(f"Phase '{phase}' budget exceeded: ${phase_spent + cost:.2f} > ${phase_budget:.2f}")
                return False

        return True

    def record_cost(self, cost: float, phase: Optional[str] = None):
        """
        Record cost spent.

        Args:
            cost: Cost to record
            phase: Optional phase name
        """
        self.spent += cost

        if phase:
            self.phase_spent[phase] = self.phase_spent.get(phase, 0.0) + cost

        # Log if approaching budget
        if self.spent > self.total_budget * 0.8:
            remaining = self.total_budget - self.spent
            self.logger.warning(f"Budget alert: ${remaining:.2f} remaining")

    def get_budget_status(self) -> Dict[str, Any]:
        """
        Get budget status.

        Returns:
            Budget status dictionary
        """
        return {
            'total_budget': self.total_budget,
            'spent': self.spent,
            'remaining': self.total_budget - self.spent,
            'utilization_pct': (self.spent / self.total_budget * 100) if self.total_budget > 0 else 0,
            'phase_budgets': {
                phase: {
                    'allocated': self.total_budget * pct,
                    'spent': self.phase_spent.get(phase, 0.0),
                    'remaining': self.total_budget * pct - self.phase_spent.get(phase, 0.0)
                }
                for phase, pct in self.phase_budgets.items()
            }
        }


class CostPredictor:
    """
    Predicts evaluation cost before execution.

    Uses historical data and scenario parameters to estimate cost.
    """

    def __init__(self):
        """Initialize cost predictor."""
        self.historical_costs: Dict[str, List[float]] = {}  # scenario → costs

    def predict(
        self,
        scenario_name: str,
        num_rounds: int,
        llm_mode: str,
        population_size: int = 50
    ) -> Dict[str, float]:
        """
        Predict evaluation cost.

        Args:
            scenario_name: Scenario name
            num_rounds: Number of evaluation rounds
            llm_mode: LLM mode ('none', 'cheap', 'multi')
            population_size: Population size for mutations

        Returns:
            Cost prediction with breakdown
        """
        # Base costs per round (empirical averages)
        base_costs = {
            'none': 0.0,
            'cheap': 0.50,   # ~$0.50 per round with cheap LLM
            'multi': 1.50    # ~$1.50 per round with multi-LLM
        }

        # Scenario-specific multipliers
        scenario_multipliers = {
            'sql_injection': 1.0,
            'xss': 1.2,
            'ddos': 0.8,
            'command_injection': 1.1
        }

        # Calculate prediction
        base_cost_per_round = base_costs.get(llm_mode, 0.5)
        scenario_mult = scenario_multipliers.get(scenario_name, 1.0)
        population_mult = population_size / 50.0  # Normalized to 50

        predicted_cost = (
            base_cost_per_round *
            num_rounds *
            scenario_mult *
            population_mult
        )

        # Add variance (±20%)
        min_cost = predicted_cost * 0.8
        max_cost = predicted_cost * 1.2

        return {
            'predicted_cost': predicted_cost,
            'min_cost': min_cost,
            'max_cost': max_cost,
            'cost_per_round': predicted_cost / num_rounds,
            'confidence': 0.8 if scenario_name in scenario_multipliers else 0.5
        }

    def update(self, scenario_name: str, actual_cost: float):
        """
        Update predictor with actual cost.

        Args:
            scenario_name: Scenario name
            actual_cost: Actual cost observed
        """
        if scenario_name not in self.historical_costs:
            self.historical_costs[scenario_name] = []

        self.historical_costs[scenario_name].append(actual_cost)


# ============================================================================
# EXAMPLE MODELS
# ============================================================================

# Example LLM models (replace with actual models)
EXAMPLE_MODELS = [
    LLMModel(
        name='gpt-3.5-turbo',
        cost_per_1k_tokens=0.0015,
        avg_quality_score=0.7,
        avg_latency_ms=800,
        context_window=16000
    ),
    LLMModel(
        name='gpt-4o-mini',
        cost_per_1k_tokens=0.150 / 1000,
        avg_quality_score=0.85,
        avg_latency_ms=1200,
        context_window=128000
    ),
    LLMModel(
        name='gpt-4o',
        cost_per_1k_tokens=2.5 / 1000,
        avg_quality_score=0.95,
        avg_latency_ms=2000,
        context_window=128000
    ),
]
