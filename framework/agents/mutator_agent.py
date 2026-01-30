"""
Mutator Agent - Evolutionary attack optimization.

Implements diversity-preserving evolution with novelty search (Enhancement 2).
Uses genetic algorithm with Pareto selection for multi-objective optimization.
"""

from typing import Any, Dict, List, Optional, Set, Tuple
import random
from datetime import datetime
from collections import defaultdict

from ..base import UnifiedAgent, AgentCapabilities, Capability, AgentRole, Task, KnowledgeBase, PurpleAgent, Mutator
from ..models import Attack, TestResult, BehaviorDescriptor


class MutatorAgent(UnifiedAgent):
    """
    Agent that evolves attacks using genetic algorithms with novelty search.

    Uses diversity-preserving evolution to discover diverse attack families.
    """

    def __init__(
        self,
        agent_id: str,
        knowledge_base: KnowledgeBase,
        scenario: 'SecurityScenario',
        population_size: int = 50,
        mutation_rate: float = 0.3,
        novelty_weight: float = 0.5,
        llm_client: Optional[Any] = None,
        model_router: Optional[Any] = None,
        llm_mutation_ratio: float = 0.3
    ):
        """
        Initialize mutator agent.

        Args:
            agent_id: Unique agent identifier
            knowledge_base: Shared knowledge base
            scenario: Security scenario
            population_size: Size of attack population
            mutation_rate: Probability of mutation
            novelty_weight: Weight for novelty vs evasion (0-1)
            llm_client: Optional LLM client for creative mutations
            model_router: Optional model router for cost optimization
            llm_mutation_ratio: Ratio of LLM vs algorithmic mutations (0-1)
        """
        capabilities = AgentCapabilities(
            capabilities={Capability.MUTATE},
            role=AgentRole.MUTATOR,
            requires_llm=llm_client is not None,
            cost_per_invocation=0.05 if llm_client else 0.0,
            avg_latency_ms=1500.0 if llm_client else 200.0
        )
        super().__init__(agent_id, capabilities, knowledge_base)
        self.scenario = scenario
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.novelty_weight = novelty_weight
        self.llm_client = llm_client
        self.model_router = model_router
        self.llm_mutation_ratio = llm_mutation_ratio

        # Evolution state
        self.population: List[Attack] = []
        self.novelty_archive: List[BehaviorDescriptor] = []
        self.generation = 0
        self.fitness_history: List[Dict[str, float]] = []

        # Get mutators from scenario
        self.mutators = scenario.get_mutators()

    def execute_task(self, task: Task) -> Any:
        """
        Execute mutation task.

        Args:
            task: Task with parameters:
                - attacks: Initial population
                - purple_agent: Target agent
                - num_generations: Number of generations
                - target_technique: Optional technique filter

        Returns:
            Dictionary with evolved population
        """
        initial_attacks = task.parameters.get('attacks', [])
        purple_agent = task.parameters.get('purple_agent')
        num_generations = task.parameters.get('num_generations', 10)

        if not purple_agent:
            self.logger.error("Missing required parameter: purple_agent")
            return {'error': 'Missing purple_agent'}

        # Initialize population
        if not self.population and initial_attacks:
            self.population = initial_attacks[:self.population_size]

        # Evolve
        for gen in range(num_generations):
            self.generation = gen
            self._evolve_generation(purple_agent)

        # Share knowledge
        self.share_knowledge(
            entry_type='mutation',
            data={
                'generation': self.generation,
                'population_size': len(self.population),
                'num_attack_families': len(set(self._get_attack_family(a) for a in self.population)),
                'best_fitness': max(self.fitness_history[-1].values()) if self.fitness_history else 0.0
            },
            tags={'mutation', 'evolution'}
        )

        return {
            'evolved_attacks': self.population,
            'generation': self.generation,
            'novelty_archive_size': len(self.novelty_archive)
        }

    def _evolve_generation(self, purple_agent: PurpleAgent):
        """
        Evolve one generation.

        Args:
            purple_agent: Target agent for fitness evaluation
        """
        self.logger.info(f"Evolving generation {self.generation}")

        # 1. Evaluate fitness (evasion + novelty)
        fitness_scores = self._evaluate_fitness(purple_agent)

        # 2. Select parents using Pareto selection
        parents = self._pareto_selection(fitness_scores)

        # 3. Generate offspring
        offspring = []
        while len(offspring) < self.population_size:
            # Select two parents
            parent1, parent2 = random.sample(parents, 2)

            # Crossover
            child = self._crossover(parent1, parent2)

            # Mutation
            if random.random() < self.mutation_rate:
                child = self._mutate(child)

            offspring.append(child)

        # 4. Replace population
        self.population = offspring[:self.population_size]

        # 5. Update novelty archive
        self._update_novelty_archive()

        # 6. Record fitness
        avg_fitness = sum(f['total'] for f in fitness_scores.values()) / len(fitness_scores) if fitness_scores else 0.0
        self.fitness_history.append({'generation': self.generation, 'avg_fitness': avg_fitness})

    def _evaluate_fitness(self, purple_agent: PurpleAgent) -> Dict[str, Dict[str, float]]:
        """
        Evaluate fitness of population.

        Fitness = evasion_fitness * (1 - novelty_weight) + novelty_fitness * novelty_weight

        Args:
            purple_agent: Target agent

        Returns:
            Dictionary mapping attack_id to fitness scores
        """
        fitness_scores = {}

        for attack in self.population:
            # 1. Evasion fitness (does it evade detection?)
            result = self.scenario.execute_attack(attack, purple_agent)
            evasion_fitness = 0.0 if result.detected else 1.0

            # 2. Novelty fitness (how novel is the behavior?)
            descriptor = BehaviorDescriptor.extract(attack.payload, attack.metadata)
            novelty_fitness = self._calculate_novelty(descriptor)

            # 3. Combined fitness
            total_fitness = (
                evasion_fitness * (1 - self.novelty_weight) +
                novelty_fitness * self.novelty_weight
            )

            fitness_scores[attack.attack_id] = {
                'evasion': evasion_fitness,
                'novelty': novelty_fitness,
                'total': total_fitness
            }

        return fitness_scores

    def _calculate_novelty(self, descriptor: BehaviorDescriptor) -> float:
        """
        Calculate novelty score using k-nearest neighbors.

        Args:
            descriptor: Behavior descriptor

        Returns:
            Novelty score [0, 1]
        """
        if not self.novelty_archive:
            return 1.0  # First attack is maximally novel

        # Calculate distances to k nearest neighbors
        k = min(15, len(self.novelty_archive))
        distances = [
            descriptor.distance(archive_desc)
            for archive_desc in self.novelty_archive
        ]
        distances.sort()

        # Novelty = average distance to k nearest neighbors
        novelty = sum(distances[:k]) / k

        # Normalize to [0, 1] (heuristic: divide by max expected distance)
        max_distance = 10.0  # Tunable parameter
        return min(1.0, novelty / max_distance)

    def _pareto_selection(self, fitness_scores: Dict[str, Dict[str, float]]) -> List[Attack]:
        """
        Select parents using Pareto dominance.

        Args:
            fitness_scores: Fitness scores for population

        Returns:
            Selected parents
        """
        # Get Pareto front (non-dominated solutions)
        pareto_front = []

        for attack in self.population:
            scores = fitness_scores[attack.attack_id]
            is_dominated = False

            # Check if this attack is dominated by any other
            for other_attack in self.population:
                if other_attack.attack_id == attack.attack_id:
                    continue

                other_scores = fitness_scores[other_attack.attack_id]

                # Check dominance (other is better in both objectives)
                if (other_scores['evasion'] >= scores['evasion'] and
                    other_scores['novelty'] >= scores['novelty'] and
                    (other_scores['evasion'] > scores['evasion'] or
                     other_scores['novelty'] > scores['novelty'])):
                    is_dominated = True
                    break

            if not is_dominated:
                pareto_front.append(attack)

        # If Pareto front is too small, add high-fitness individuals
        if len(pareto_front) < self.population_size // 2:
            # Sort by total fitness
            sorted_attacks = sorted(
                self.population,
                key=lambda a: fitness_scores[a.attack_id]['total'],
                reverse=True
            )
            for attack in sorted_attacks:
                if attack not in pareto_front:
                    pareto_front.append(attack)
                if len(pareto_front) >= self.population_size // 2:
                    break

        return pareto_front

    def _crossover(self, parent1: Attack, parent2: Attack) -> Attack:
        """
        Perform crossover between two parents.

        Args:
            parent1, parent2: Parent attacks

        Returns:
            Child attack
        """
        # Simple crossover: Mix payloads
        # (Should be overridden in scenario-specific implementations)

        # For now, randomly choose one parent's payload
        parent = random.choice([parent1, parent2])

        child = self.scenario.create_attack(
            technique=parent.technique,
            payload=parent.payload,
            metadata={
                'generation': self.generation,
                'parent1': parent1.attack_id,
                'parent2': parent2.attack_id,
                'operation': 'crossover'
            }
        )
        child.parent_attack_id = parent.attack_id
        child.generation = self.generation
        child.created_by = self.agent_id

        return child

    def _mutate(self, attack: Attack) -> Attack:
        """
        Mutate an attack using hybrid algorithmic + LLM approach.

        Args:
            attack: Attack to mutate

        Returns:
            Mutated attack
        """
        # Hybrid mutation: Use LLM for creative mutations, algorithmic for systematic ones
        use_llm = (self.llm_client is not None and
                   random.random() < self.llm_mutation_ratio)

        if use_llm:
            return self._llm_mutate(attack)
        else:
            return self._algorithmic_mutate(attack)

    def _algorithmic_mutate(self, attack: Attack) -> Attack:
        """
        Algorithmic mutation using scenario mutators.

        Args:
            attack: Attack to mutate

        Returns:
            Mutated attack
        """
        # Choose random mutator
        if not self.mutators:
            return attack

        mutator = random.choice(self.mutators)

        # Apply mutation
        mutated_attacks = mutator.mutate(attack)

        if mutated_attacks:
            mutated = random.choice(mutated_attacks)
            mutated.generation = self.generation
            mutated.mutation_type = mutator.get_mutation_type()
            mutated.parent_attack_id = attack.attack_id
            mutated.created_by = self.agent_id
            return mutated

        return attack

    def _llm_mutate(self, attack: Attack) -> Attack:
        """
        LLM-based creative mutation.

        Uses LLM to suggest novel attack variations.

        Args:
            attack: Attack to mutate

        Returns:
            Mutated attack with LLM-suggested variation
        """
        prompt = f"""You are a security researcher testing detection systems.

Original attack payload:
{attack.payload}

Attack technique: {attack.technique}
Scenario: {self.scenario.name}

Generate a creative mutation of this attack that:
1. Maintains the same attack intent and technique
2. Uses obfuscation, encoding, or alternative syntax
3. Is novel and likely to evade basic pattern matching
4. Is still valid and executable

Provide ONLY the mutated payload, no explanations.
"""

        try:
            # Route to appropriate model if router available
            if self.model_router:
                task = Task(
                    task_id=f"mutate_{attack.attack_id}_{datetime.now().timestamp()}",
                    task_type='mutate',
                    description=f"Generate creative mutation",
                    parameters={'attack_id': attack.attack_id}
                )
                model_client = self.model_router.route(task, prompt)
                self.logger.info(f"Routed to model: {model_client.name}")
            else:
                model_client = self.llm_client

            response = model_client.generate(
                prompt=prompt,
                max_tokens=200,
                temperature=0.9  # High temperature for creativity
            )

            # Parse response - extract just the payload
            mutated_payload = response.content.strip()

            # Remove markdown code blocks if present
            if '```' in mutated_payload:
                lines = mutated_payload.split('\n')
                mutated_payload = '\n'.join([l for l in lines if not l.startswith('```')])
                mutated_payload = mutated_payload.strip()

            # Create mutated attack
            mutated = self.scenario.create_attack(
                technique=attack.technique,
                payload=mutated_payload,
                metadata={
                    'generation': self.generation,
                    'parent': attack.attack_id,
                    'mutation_type': 'llm_creative',
                    'llm_model': model_client.model if hasattr(model_client, 'model') else 'unknown'
                }
            )
            mutated.parent_attack_id = attack.attack_id
            mutated.generation = self.generation
            mutated.mutation_type = 'llm_creative'
            mutated.created_by = self.agent_id

            # Update router with quality feedback
            if self.model_router:
                # Quality: mutation should be different from original
                quality_feedback = 0.8 if mutated_payload != attack.payload else 0.2
                self.model_router.update('mutate', quality_feedback)

            self.logger.info(f"LLM mutation: {attack.payload[:50]} -> {mutated_payload[:50]}")
            return mutated

        except Exception as e:
            self.logger.error(f"LLM mutation failed: {e}")
            # Fall back to algorithmic mutation
            return self._algorithmic_mutate(attack)

    def _update_novelty_archive(self):
        """Update novelty archive with novel behaviors."""
        for attack in self.population:
            descriptor = BehaviorDescriptor.extract(attack.payload, attack.metadata)

            # Add to archive if sufficiently novel
            novelty = self._calculate_novelty(descriptor)
            if novelty > 0.7:  # Threshold for archive inclusion
                self.novelty_archive.append(descriptor)

        # Limit archive size
        max_archive_size = 1000
        if len(self.novelty_archive) > max_archive_size:
            # Keep most recent
            self.novelty_archive = self.novelty_archive[-max_archive_size:]

    def _get_attack_family(self, attack: Attack) -> str:
        """
        Get attack family label.

        Args:
            attack: Attack to classify

        Returns:
            Family label
        """
        # Simple clustering by technique and mutation type
        return f"{attack.technique}_{attack.mutation_type or 'base'}"

    def can_execute(self, task: Task) -> bool:
        """Check if agent can execute task."""
        return task.task_type in ['mutate', 'evolve']

    def get_evolution_stats(self) -> Dict[str, Any]:
        """
        Get evolution statistics.

        Returns:
            Dictionary with evolution stats
        """
        return {
            'generation': self.generation,
            'population_size': len(self.population),
            'novelty_archive_size': len(self.novelty_archive),
            'num_attack_families': len(set(self._get_attack_family(a) for a in self.population)),
            'fitness_history': self.fitness_history
        }
