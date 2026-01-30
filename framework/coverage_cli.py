#!/usr/bin/env python3
"""
Coverage CLI - Command-line tool for MITRE ATT&CK coverage tracking.

Usage:
    python -m framework.coverage_cli report <scenario>
    python -m framework.coverage_cli suggest <scenario>
    python -m framework.coverage_cli template <technique>
"""

import sys
import json
import argparse
from typing import Optional

from .base import SecurityScenario
from .coverage_tracker import CoverageTracker, CoverageExpansionAgent


def load_scenario(scenario_name: str) -> Optional[SecurityScenario]:
    """
    Load scenario by name.

    Args:
        scenario_name: Name of scenario module

    Returns:
        Scenario instance or None
    """
    try:
        if scenario_name == 'sql_injection':
            from ..scenarios.sql_injection import SQLInjectionScenario
            return SQLInjectionScenario()
        # Add more scenarios here as they are implemented
        else:
            print(f"❌ Unknown scenario: {scenario_name}")
            print("Available scenarios: sql_injection")
            return None
    except Exception as e:
        print(f"❌ Failed to load scenario '{scenario_name}': {e}")
        return None


def cmd_report(args):
    """Show coverage report for scenario."""
    scenario = load_scenario(args.scenario)
    if not scenario:
        return 1

    tracker = CoverageTracker(scenario=scenario, taxonomy='MITRE_ATT&CK')
    report = tracker.generate_coverage_report()

    print("\n" + "="*60)
    print(f"📊 MITRE ATT&CK Coverage Report: {args.scenario}")
    print("="*60)

    summary = report['coverage_summary']
    print(f"\n📈 Coverage Summary:")
    print(f"   Total techniques: {summary['total_techniques']}")
    print(f"   Covered: {summary['covered']} ({summary['coverage_percentage']:.1f}%)")
    print(f"   Partially covered: {summary['partially_covered']}")
    print(f"   Uncovered: {summary['uncovered']}")

    if report['covered_techniques']:
        print(f"\n✅ Covered Techniques ({len(report['covered_techniques'])}):")
        for tech in report['covered_techniques'][:10]:
            print(f"   • {tech}")
        if len(report['covered_techniques']) > 10:
            print(f"   ... and {len(report['covered_techniques']) - 10} more")

    if report['partially_covered_techniques']:
        print(f"\n⚠️  Partially Covered Techniques ({len(report['partially_covered_techniques'])}):")
        for item in report['partially_covered_techniques'][:5]:
            print(f"   • {item['technique']}: {item['coverage_pct']:.0f}%")
        if len(report['partially_covered_techniques']) > 5:
            print(f"   ... and {len(report['partially_covered_techniques']) - 5} more")

    if report['priority_next_techniques']:
        print(f"\n🎯 Priority Next Techniques:")
        for item in report['priority_next_techniques'][:5]:
            print(f"   • {item['technique']} (priority: {item['priority']:.2f})")

    debt = report['coverage_debt']
    print(f"\n📉 Coverage Debt:")
    print(f"   Total uncovered: {debt['total_debt']}")
    print(f"   High priority: {debt['high_priority_debt']}")
    print(f"   Estimated time to full coverage: {debt['estimated_time_to_full_coverage']}")

    print("\n" + "="*60)

    if args.json:
        with open(args.json, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"📄 Full report saved to: {args.json}")

    return 0


def cmd_suggest(args):
    """Suggest next scenario to implement."""
    scenario = load_scenario(args.scenario)
    if not scenario:
        return 1

    tracker = CoverageTracker(scenario=scenario, taxonomy='MITRE_ATT&CK')
    agent = CoverageExpansionAgent(tracker)

    suggestion = agent.suggest_next_scenario()

    print("\n" + "="*60)
    print(f"💡 Next Scenario Suggestion: {args.scenario}")
    print("="*60)

    if suggestion.get('suggestion') is None:
        print("\n🎉 Full coverage achieved!")
        return 0

    print(f"\n🎯 Suggested Technique: {suggestion['suggested_technique']}")
    print(f"   Priority Score: {suggestion['priority_score']:.2f}")
    print(f"   Coverage Impact: {suggestion['coverage_impact']} techniques")

    print(f"\n📋 Sub-techniques:")
    for sub_tech in suggestion['sub_techniques']:
        print(f"   • {sub_tech}")

    guide = suggestion['implementation_guide']
    print(f"\n📖 Implementation Guide:")
    print(f"   Estimated Time: {guide['estimated_time']}")
    print(f"   Scenario Class: {guide['scenario_class']}")

    print(f"\n   Required Components:")
    for component in guide['required_components']:
        print(f"   {component}")

    print(f"\n   MITRE Reference: {guide['mitre_reference']}")

    print("\n💻 Generate code template with:")
    print(f"   python -m framework.coverage_cli template {suggestion['suggested_technique']}")

    print("\n" + "="*60)

    if args.json:
        with open(args.json, 'w') as f:
            json.dump(suggestion, f, indent=2)
        print(f"📄 Suggestion saved to: {args.json}")

    return 0


def cmd_template(args):
    """Generate scenario template."""
    # Dummy scenario for template generation
    from ..scenarios.sql_injection import SQLInjectionScenario
    scenario = SQLInjectionScenario()

    tracker = CoverageTracker(scenario=scenario, taxonomy='MITRE_ATT&CK')
    agent = CoverageExpansionAgent(tracker)

    template = agent.generate_scenario_template(args.technique)

    print("\n" + "="*60)
    print(f"📝 Scenario Template: {args.technique}")
    print("="*60)

    if args.output:
        with open(args.output, 'w') as f:
            f.write(template)
        print(f"\n✅ Template saved to: {args.output}")
    else:
        print()
        print(template)

    print("\n" + "="*60)
    print(f"📖 Next Steps:")
    print(f"   1. Implement the TODOs in the template")
    print(f"   2. Add attack datasets")
    print(f"   3. Test with baseline purple agent")
    print(f"   4. Register scenario in framework")
    print("="*60)

    return 0


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='MITRE ATT&CK Coverage Tracking Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # Report command
    report_parser = subparsers.add_parser('report', help='Show coverage report')
    report_parser.add_argument('scenario', help='Scenario name (e.g., sql_injection)')
    report_parser.add_argument('--json', help='Save report to JSON file')

    # Suggest command
    suggest_parser = subparsers.add_parser('suggest', help='Suggest next scenario')
    suggest_parser.add_argument('scenario', help='Scenario name (e.g., sql_injection)')
    suggest_parser.add_argument('--json', help='Save suggestion to JSON file')

    # Template command
    template_parser = subparsers.add_parser('template', help='Generate scenario template')
    template_parser.add_argument('technique', help='MITRE technique ID (e.g., T1234)')
    template_parser.add_argument('--output', '-o', help='Output file path')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Execute command
    if args.command == 'report':
        return cmd_report(args)
    elif args.command == 'suggest':
        return cmd_suggest(args)
    elif args.command == 'template':
        return cmd_template(args)
    else:
        print(f"❌ Unknown command: {args.command}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
