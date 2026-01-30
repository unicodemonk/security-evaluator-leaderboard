"""
Coverage Tracker - Systematic MITRE ATT&CK coverage expansion.

Tracks which techniques are covered, identifies gaps, prioritizes
uncovered techniques for systematic expansion.
"""

from typing import Any, Dict, List, Optional, Set, Tuple
from datetime import datetime
import logging

from .base import SecurityScenario
from .models import CoverageReport, EvaluationResult, Attack


class CoverageTracker:
    """
    Tracks coverage of attack techniques against taxonomies.

    Supports:
    - MITRE ATT&CK
    - OWASP Top 10
    - Custom taxonomies
    """

    def __init__(
        self,
        scenario: SecurityScenario,
        taxonomy: str = 'MITRE_ATT&CK'
    ):
        """
        Initialize coverage tracker.

        Args:
            scenario: Security scenario
            taxonomy: Taxonomy to track (e.g., 'MITRE_ATT&CK')
        """
        self.scenario = scenario
        self.taxonomy = taxonomy
        self.logger = logging.getLogger("CoverageTracker")

        # Get MITRE mapping from scenario
        self.mitre_mapping = scenario.get_mitre_mapping()

        # Initialize coverage report
        self.coverage_report = self._initialize_coverage()

    def _initialize_coverage(self) -> CoverageReport:
        """Initialize coverage report."""

        # Get all MITRE techniques from mapping
        all_techniques = set()
        for scenario_tech, mitre_techs in self.mitre_mapping.items():
            all_techniques.update(mitre_techs)

        return CoverageReport(
            taxonomy=self.taxonomy,
            total_techniques=len(all_techniques),
            covered_techniques=set(),
            uncovered_techniques=all_techniques.copy(),
            partially_covered={},
            priority_queue=[]
        )

    def update_coverage(self, evaluation_result: EvaluationResult):
        """
        Update coverage based on evaluation results.

        Args:
            evaluation_result: Completed evaluation result
        """
        self.logger.info("Updating coverage from evaluation results")

        # Analyze which techniques were tested
        tested_techniques: Dict[str, int] = {}  # technique → num_tests

        for attack in evaluation_result.attacks:
            # First, try to get MITRE technique directly from attack metadata
            mitre_tech_id = None
            if hasattr(attack, 'metadata') and isinstance(attack.metadata, dict):
                mitre_tech_id = attack.metadata.get('mitre_technique_id')
            
            if mitre_tech_id:
                # Direct MITRE mapping from metadata
                tested_techniques[mitre_tech_id] = tested_techniques.get(mitre_tech_id, 0) + 1
            elif hasattr(attack, 'technique') and attack.technique:
                # Fallback: Get MITRE techniques from scenario mapping
                mitre_techs = self.mitre_mapping.get(attack.technique, [])
                for mitre_tech in mitre_techs:
                    tested_techniques[mitre_tech] = tested_techniques.get(mitre_tech, 0) + 1

        self.logger.info(f"Found {len(tested_techniques)} unique MITRE techniques tested")

        # Update coverage status
        for mitre_tech, num_tests in tested_techniques.items():
            if num_tests >= 10:
                # Fully covered (10+ tests)
                self.coverage_report.covered_techniques.add(mitre_tech)
                self.coverage_report.uncovered_techniques.discard(mitre_tech)

                # Remove from partially covered
                if mitre_tech in self.coverage_report.partially_covered:
                    del self.coverage_report.partially_covered[mitre_tech]

            elif num_tests >= 3:
                # Partially covered (3-9 tests)
                coverage_pct = min(100.0, (num_tests / 10.0) * 100)
                self.coverage_report.partially_covered[mitre_tech] = coverage_pct

                # Still in uncovered (move to covered once 10+ tests)

        # Recalculate coverage percentage
        self.coverage_report.calculate_coverage()

        self.logger.info(f"Coverage: {self.coverage_report.coverage_percentage:.1f}% "
                        f"({len(self.coverage_report.covered_techniques)}/{self.coverage_report.total_techniques})")

    def prioritize_next_techniques(self, top_n: int = 5) -> List[Tuple[str, float]]:
        """
        Prioritize next techniques to implement.

        Uses coverage-debt algorithm:
        - High priority: Uncovered techniques that are related to current attacks
        - Medium priority: Partially covered techniques
        - Low priority: Unrelated uncovered techniques

        Args:
            top_n: Number of techniques to return

        Returns:
            List of (technique, priority_score) tuples
        """
        priorities = []

        # Current scenario techniques
        current_techniques = set(self.scenario.get_techniques())

        # Get MITRE techniques for current attacks
        current_mitre = set()
        for tech in current_techniques:
            current_mitre.update(self.mitre_mapping.get(tech, []))

        # Priority 1: Related uncovered techniques (same tactic)
        for uncovered_tech in self.coverage_report.uncovered_techniques:
            # Check if related to current attacks
            is_related = self._is_related(uncovered_tech, current_mitre)

            if is_related:
                priority = 0.9  # High priority
            else:
                priority = 0.3  # Low priority

            priorities.append((uncovered_tech, priority))

        # Priority 2: Partially covered techniques (finish them)
        for partial_tech, coverage_pct in self.coverage_report.partially_covered.items():
            # Priority inversely proportional to coverage
            priority = 0.7 * (1 - coverage_pct / 100.0)
            priorities.append((partial_tech, priority))

        # Sort by priority
        priorities.sort(key=lambda x: x[1], reverse=True)

        # Update priority queue
        self.coverage_report.priority_queue = priorities[:top_n]

        return priorities[:top_n]

    def _is_related(self, technique: str, reference_techniques: Set[str]) -> bool:
        """
        Check if technique is related to reference techniques.

        Uses MITRE ATT&CK hierarchy (same tactic).

        Args:
            technique: Technique to check
            reference_techniques: Reference techniques

        Returns:
            True if related
        """
        # Extract tactic from technique ID
        # MITRE format: T1234 or T1234.001
        tech_id = technique.split('.')[0]

        for ref_tech in reference_techniques:
            ref_id = ref_tech.split('.')[0]

            # Same base technique
            if tech_id == ref_id:
                return True

            # TODO: Use MITRE ATT&CK taxonomy to check same tactic
            # For now, use simple heuristic

        return False

    def generate_coverage_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive coverage report.

        Returns:
            Coverage report dictionary
        """
        return {
            'taxonomy': self.coverage_report.taxonomy,
            'timestamp': datetime.now().isoformat(),

            'coverage_summary': {
                'total_techniques': self.coverage_report.total_techniques,
                'covered': len(self.coverage_report.covered_techniques),
                'partially_covered': len(self.coverage_report.partially_covered),
                'uncovered': len(self.coverage_report.uncovered_techniques),
                'coverage_percentage': self.coverage_report.coverage_percentage
            },

            'covered_techniques': list(self.coverage_report.covered_techniques),

            'partially_covered_techniques': [
                {'technique': tech, 'coverage_pct': pct}
                for tech, pct in self.coverage_report.partially_covered.items()
            ],

            'priority_next_techniques': [
                {'technique': tech, 'priority': pri}
                for tech, pri in self.coverage_report.priority_queue
            ],

            'coverage_debt': {
                'total_debt': len(self.coverage_report.uncovered_techniques),
                'high_priority_debt': len([t for t, p in self.coverage_report.priority_queue if p > 0.7]),
                'estimated_time_to_full_coverage': self._estimate_time_to_coverage()
            }
        }
    
    def get_coverage_report(self) -> Dict[str, Any]:
        """
        Alias for generate_coverage_report() for API compatibility.

        Returns:
            Coverage report dictionary
        """
        return self.generate_coverage_report()

    def _estimate_time_to_coverage(self) -> str:
        """
        Estimate time to achieve full coverage.

        Assumes 4-6 hours per new technique.

        Returns:
            Time estimate string
        """
        uncovered = len(self.coverage_report.uncovered_techniques)
        partially = len(self.coverage_report.partially_covered)

        # Uncovered: 4-6 hours each
        # Partially: 2-3 hours to complete
        total_hours = uncovered * 5 + partially * 2.5

        if total_hours < 40:
            return f"{int(total_hours)} hours (~{int(total_hours / 8)} days)"
        elif total_hours < 160:
            return f"~{int(total_hours / 40)} weeks"
        else:
            return f"~{int(total_hours / 160)} months"


class CoverageExpansionAgent:
    """
    Agent that automatically suggests next scenarios to implement.

    Reads coverage report and generates implementation suggestions.
    """

    def __init__(self, coverage_tracker: CoverageTracker):
        """
        Initialize expansion agent.

        Args:
            coverage_tracker: Coverage tracker instance
        """
        self.coverage_tracker = coverage_tracker
        self.logger = logging.getLogger("CoverageExpansionAgent")

    def suggest_next_scenario(self) -> Dict[str, Any]:
        """
        Suggest next scenario to implement.

        Returns:
            Suggestion dictionary with implementation details
        """
        # Get priority techniques
        priorities = self.coverage_tracker.prioritize_next_techniques(top_n=10)

        if not priorities:
            return {'suggestion': None, 'reason': 'Full coverage achieved!'}

        # Group by base technique
        technique_groups: Dict[str, List[str]] = {}
        for tech, priority in priorities:
            base_tech = tech.split('.')[0]
            if base_tech not in technique_groups:
                technique_groups[base_tech] = []
            technique_groups[base_tech].append(tech)

        # Select most impactful group
        best_group = max(technique_groups.items(), key=lambda x: len(x[1]))
        base_tech, sub_techs = best_group

        # Generate suggestion
        suggestion = {
            'suggested_technique': base_tech,
            'sub_techniques': sub_techs,
            'priority_score': sum(p for t, p in priorities if t in sub_techs) / len(sub_techs),
            'coverage_impact': len(sub_techs),

            'implementation_guide': {
                'scenario_class': f"{base_tech.replace('T', '')}Scenario",
                'estimated_time': '4-6 hours',
                'required_components': [
                    '1. Implement SecurityScenario interface',
                    '2. Define attack techniques',
                    '3. Create 2-3 mutators',
                    '4. Create 2 validators',
                    '5. Implement baseline dataset (optional)'
                ],
                'example_techniques': sub_techs[:3],
                'mitre_reference': f"https://attack.mitre.org/techniques/{base_tech}/"
            }
        }

        return suggestion

    def generate_scenario_template(self, technique: str) -> str:
        """
        Generate Python code template for new scenario.

        Args:
            technique: MITRE technique ID

        Returns:
            Python code template
        """
        template = f'''"""
{technique} Scenario - Implementation for Unified Framework.

MITRE ATT&CK: {technique}
Reference: https://attack.mitre.org/techniques/{technique}/
"""

from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime

from framework.base import SecurityScenario, Mutator, Validator, PurpleAgent
from framework.models import Attack, TestResult, create_attack_id, calculate_outcome


# ============================================================================
# MUTATORS
# ============================================================================

class {technique.replace('T', '')}Mutator(Mutator):
    """TODO: Implement mutator"""

    def mutate(self, attack: Attack) -> List[Attack]:
        # TODO: Implement mutation logic
        return []

    def get_mutation_type(self) -> str:
        return '{technique.lower()}_mutation'


# ============================================================================
# VALIDATORS
# ============================================================================

class {technique.replace('T', '')}Validator(Validator):
    """TODO: Implement validator"""

    def validate(self, attack: Attack) -> Tuple[bool, Optional[str]]:
        # TODO: Implement validation logic
        return True, None

    def get_validator_type(self) -> str:
        return 'syntax'


# ============================================================================
# SCENARIO
# ============================================================================

class {technique.replace('T', '')}Scenario(SecurityScenario):
    """
    {technique} scenario implementation.
    """

    def get_name(self) -> str:
        return '{technique.lower()}'

    def get_techniques(self) -> List[str]:
        # TODO: Define sub-techniques
        return ['technique_1', 'technique_2']

    def get_mutators(self) -> List[Mutator]:
        return [{technique.replace('T', '')}Mutator()]

    def get_validators(self) -> List[Validator]:
        return [{technique.replace('T', '')}Validator()]

    def create_attack(self, technique: str, payload: Any, metadata: Dict[str, Any]) -> Attack:
        return Attack(
            attack_id=create_attack_id('{technique.lower()}', technique, datetime.now()),
            scenario='{technique.lower()}',
            technique=technique,
            payload=payload,
            metadata=metadata
        )

    def execute_attack(self, attack: Attack, target: PurpleAgent) -> TestResult:
        return target.detect(attack)

    def get_mitre_mapping(self) -> Dict[str, List[str]]:
        return {{
            'technique_1': ['{technique}'],
            'technique_2': ['{technique}.001']
        }}
'''

        return template
