#!/usr/bin/env python3
"""
Simple SQL Injection Evaluation Example

Demonstrates how to use the Unified Framework to evaluate a SQL injection detector.
"""

import sys
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ecosystem import create_ecosystem
from scenarios.sql_injection import SQLInjectionScenario, SimplePatternPurpleAgent


def main():
    """Run simple SQL injection evaluation."""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    print("=" * 80)
    print("Unified Framework - SQL Injection Evaluation Example")
    print("=" * 80)
    print()

    # 1. Create scenario
    print("1. Creating SQL Injection scenario...")
    scenario = SQLInjectionScenario()
    print(f"   ✓ Techniques: {scenario.get_techniques()}")
    print(f"   ✓ Mutators: {len(scenario.get_mutators())} mutators")
    print(f"   ✓ Validators: {len(scenario.get_validators())} validators")
    print()

    # 2. Create purple agent (detector to evaluate)
    print("2. Creating Purple Agent (Simple Pattern Detector)...")
    purple_agent = SimplePatternPurpleAgent()
    print(f"   ✓ Agent: {purple_agent.get_name()}")
    print()

    # 3. Create ecosystem (NO LLM mode for fast testing)
    print("3. Creating Unified Ecosystem (NO LLM mode)...")
    ecosystem = create_ecosystem(
        scenario=scenario,
        llm_mode='none',  # No LLM for fast testing
        config={
            'num_boundary_probers': 1,
            'num_exploiters': 2,
            'num_mutators': 1,
            'population_size': 20
        }
    )
    stats = ecosystem.get_stats()
    print(f"   ✓ Agents: {stats['num_agents']}")
    print(f"   ✓ Agent roles: {stats['agents_by_role']}")
    print()

    # 4. Run evaluation
    print("4. Running Evaluation...")
    print("   (This will take ~30-60 seconds)")
    print()

    result = ecosystem.evaluate(
        purple_agent=purple_agent,
        max_rounds=5,  # Short evaluation for demo
        budget_usd=None  # No budget limit
    )

    # 5. Display results
    print()
    print("=" * 80)
    print("EVALUATION RESULTS")
    print("=" * 80)
    print()

    print(f"Purple Agent: {result.purple_agent}")
    print(f"Scenario: {result.scenario}")
    print(f"Total Attacks Tested: {result.total_attacks_tested}")
    print(f"Evaluation Time: {result.total_time_seconds:.1f} seconds")
    print(f"Total Cost: ${result.total_cost_usd:.2f}")
    print()

    print("METRICS:")
    print(f"  Precision:  {result.metrics.precision:.3f}")
    print(f"  Recall:     {result.metrics.recall:.3f}")
    print(f"  F1 Score:   {result.metrics.f1_score:.3f}")
    print(f"  Accuracy:   {result.metrics.accuracy:.3f}")
    print()

    print("CONFUSION MATRIX:")
    print(f"  True Positives:  {result.metrics.true_positives}")
    print(f"  True Negatives:  {result.metrics.true_negatives}")
    print(f"  False Positives: {result.metrics.false_positives}")
    print(f"  False Negatives: {result.metrics.false_negatives} (EVASIONS!)")
    print()

    if result.metrics.false_negatives > 0:
        print("⚠️  EVASIONS FOUND!")
        print(f"   {result.metrics.false_negatives} attacks evaded detection")
        print()

        # Show some evasions
        evasions = result.get_evasions()
        if evasions:
            print("   Sample evasions:")
            for i, evasion in enumerate(evasions[:3], 1):
                attack = next((a for a in result.attacks if a.attack_id == evasion.attack_id), None)
                if attack:
                    print(f"   {i}. {attack.technique}: {attack.payload}")

    print()
    print("AGENT CONTRIBUTIONS:")
    for agent_id, count in sorted(result.agent_contributions.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  {agent_id}: {count} contributions")

    print()
    print("=" * 80)
    print("EVALUATION COMPLETE")
    print("=" * 80)

    # 6. Save results
    output_file = "evaluation_result.json"
    print(f"\n💾 Saving results to {output_file}...")
    with open(output_file, 'w') as f:
        f.write(result.to_json())
    print(f"   ✓ Results saved")

    return result


if __name__ == '__main__':
    result = main()
    sys.exit(0)
