#!/usr/bin/env python3
"""Flatten evaluation results to match AgentBeats leaderboard format."""
import json
import sys
import re
from pathlib import Path
from collections import Counter


def main():
    if len(sys.argv) < 2:
        print("Usage: flatten_results.py <result_file> [timestamp]")
        sys.exit(1)
    
    result_file = Path(sys.argv[1])
    timestamp = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not result_file.exists():
        print(f"Error: {result_file} not found")
        sys.exit(1)
    
    with open(result_file) as f:
        data = json.load(f)
    
    # Check if already flattened (has 'results' array at top level)
    if 'results' in data and isinstance(data.get('results'), list):
        print(f'File already flattened, skipping: {result_file}')
        return
    
    # Check if this is an error result
    if 'error' in data and 'purple_agent_assessment' not in data:
        # Error case - create minimal result with agent info from error payload
        purple_agent_id = data.get('purple_agent_id', 'unknown')
        purple_agent_name = data.get('purple_agent_name', purple_agent_id)
        error_msg = data.get('error', 'Evaluation failed')
        flattened = {
            'participants': {},
            'results': [{
                'id': 'unknown',
                'purple_agent': purple_agent_name,
                'purple_agent_id': purple_agent_id,
                'score': 0,
                'accuracy': 0,
                'f1': 0,
                'precision': 0,
                'recall': 0,
                'grade': 'ERROR',
                'purple_score': 0,
                'vulnerabilities_found': 0,
                'total_tests': 0,
                'status': 'evaluation_failed',
                'error': error_msg,
                'notes': 'All tests marked invalid due to protocol/communication errors. Agent may not be compatible with evaluator protocol.'
            }]
        }
    else:
        # Normal case - extract purple agent info from evaluator output
        purple_agent_name = data.get('purple_agent_name', 'unknown')
        
        # Extract agent ID from evaluation_id which has format: eval_{uuid}_{timestamp}
        eval_id = data.get('evaluation_id', '')
        if eval_id.startswith('eval_'):
            parts = eval_id[5:]  # Remove 'eval_' prefix
            # Find last underscore followed by 8 digits (timestamp format: YYYYMMDD)
            match = re.match(r'^(.+)_(\d{8}_\d{6})$', parts)
            if match:
                purple_agent_id = match.group(1)
            else:
                purple_agent_id = parts.rsplit('_', 1)[0] if '_' in parts else parts
        else:
            purple_agent_id = 'unknown'
        
        participants = data.get('participants', {})
        
        # Get all vulnerabilities
        all_vulns = data.get('purple_agent_assessment', {}).get('vulnerabilities', [])
        
        # Generate vulnerability summary for notes field
        vuln_summary = ''
        if all_vulns:
            # Count vulnerabilities by category and severity
            category_counts = Counter()
            severity_counts = Counter()
            
            for vuln in all_vulns:
                category = vuln.get('category', 'unknown')
                severity = vuln.get('severity', 'MEDIUM')
                category_counts[category] += 1
                severity_counts[severity] += 1
            
            # Format top 3 categories
            top_categories = category_counts.most_common(3)
            category_str = ', '.join([f"{cat.replace('-', ' ').title()} ({count})" 
                                     for cat, count in top_categories])
            
            # Format severity breakdown
            severity_parts = []
            for sev in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
                if severity_counts[sev] > 0:
                    severity_parts.append(f"{sev.title()}: {severity_counts[sev]}")
            severity_str = ', '.join(severity_parts)
            
            total_vulns = len(all_vulns)
            total_tests = data.get('total_tests', 0)
            attack_rate = (total_vulns / total_tests * 100) if total_tests > 0 else 0
            
            vuln_summary = f"Found {total_vulns}/{total_tests} vulnerabilities ({attack_rate:.1f}% attack success). Top categories: {category_str}. Severity: {severity_str}."
        
        # Create structure matching SOCBench format for AgentBeats compatibility
        flattened = {
            'participants': participants,
            'results': [{
                'id': data.get('evaluation_id', 'unknown'),
                'purple_agent': purple_agent_name,
                'purple_agent_id': purple_agent_id,
                'score': data.get('purple_agent_assessment', {}).get('security_score', 0),
                'accuracy': data.get('green_agent_metrics', {}).get('accuracy', 0),
                'f1': data.get('green_agent_metrics', {}).get('f1_score', 0),
                'precision': data.get('green_agent_metrics', {}).get('precision', 0),
                'recall': data.get('green_agent_metrics', {}).get('recall', 0),
                'grade': data.get('purple_agent_assessment', {}).get('security_grade', 'N/A'),
                'purple_score': data.get('purple_agent_assessment', {}).get('security_score', 0),
                'vulnerabilities': data.get('purple_agent_assessment', {}).get('total_vulnerabilities', 0),
                'vulnerabilities_found': data.get('purple_agent_assessment', {}).get('total_vulnerabilities', 0),
                'total_tests': data.get('total_tests', 0),
                'status': 'completed',
                'error': '',
                'notes': vuln_summary,
                'created_at': timestamp
            }]
        }
    
    # Write flattened results back
    with open(result_file, 'w') as f:
        json.dump(flattened, f, indent=2)
    
    r = flattened['results'][0]
    print(f'Flattened results: Score={r["score"]:.2f}, Accuracy={r["accuracy"]:.2%}')


if __name__ == '__main__':
    main()
