#!/usr/bin/env python3
"""
Flatten evaluation results to match AgentBeats leaderboard query format.

Reads dual_evaluation JSON files and creates flattened versions with:
- id: evaluation_id
- score: green_agent_metrics.competition_score
- accuracy: green_agent_metrics.accuracy
"""

import json
import sys
from pathlib import Path

def flatten_result(input_file: Path) -> dict:
    """Flatten evaluation result to simple schema."""
    with open(input_file) as f:
        data = json.load(f)
    
    # Check if this is the new flattened format (with results array)
    if "results" in data and isinstance(data["results"], list) and len(data["results"]) > 0:
        result = data["results"][0]
        return {
            "id": result.get("id", "unknown"),
            "score": result.get("score", 0),
            "accuracy": result.get("accuracy", 0),
            "timestamp": "",
            "purple_agent": result.get("purple_agent", "unknown"),
            "purple_agent_id": result.get("purple_agent_id", "unknown"),
            "f1_score": result.get("f1", 0),
            "precision": result.get("precision", 0),
            "recall": result.get("recall", 0),
            "grade": result.get("grade", "N/A"),
            "vulnerabilities_found": result.get("vulnerabilities_found", 0),
            "total_tests": result.get("total_tests", 0),
            "status": result.get("status", ""),
            "error": result.get("error", ""),
            "notes": result.get("notes", "")
        }
    
    # Otherwise use old detailed format
    # Only count vulnerabilities that were NOT detected (actual successful attacks)
    all_vulns = data.get("purple_agent_assessment", {}).get("vulnerabilities", [])
    undetected_vulns = [v for v in all_vulns if not v.get("metadata", {}).get("detected", False)]
    
    return {
        "id": data.get("evaluation_id", "unknown"),
        "score": data.get("green_agent_metrics", {}).get("competition_score", 0),
        "accuracy": data.get("green_agent_metrics", {}).get("accuracy", 0),
        "timestamp": data.get("start_time", ""),
        "purple_agent": data.get("purple_agent_name", "unknown"),
        "f1_score": data.get("green_agent_metrics", {}).get("f1_score", 0),
        "precision": data.get("green_agent_metrics", {}).get("precision", 0),
        "recall": data.get("green_agent_metrics", {}).get("recall", 0),
        "grade": data.get("green_agent_metrics", {}).get("grade", "N/A"),
        "vulnerabilities_found": len(undetected_vulns),
        "total_tests": data.get("total_tests", 0),
        "status": "",
        "error": "",
        "notes": ""
    }

def main():
    results_dir = Path("results")
    
    if not results_dir.exists():
        print("Error: results/ directory not found")
        sys.exit(1)
    
    # Process all JSON files in results directory
    for json_file in results_dir.glob("*.json"):
        print(f"Processing {json_file.name}...")
        
        try:
            flattened = flatten_result(json_file)
            
            # Create flattened version with .flat.json suffix
            output_file = json_file.with_suffix('.flat.json')
            with open(output_file, 'w') as f:
                json.dump(flattened, f, indent=2)
            
            print(f"  Created {output_file.name}")
            print(f"    ID: {flattened['id']}")
            print(f"    Score: {flattened['score']:.2f}")
            print(f"    Accuracy: {flattened['accuracy']:.2%}")
            
        except Exception as e:
            print(f"  Error: {e}")
    
    print("\nDone! Flattened files created with .flat.json extension")

if __name__ == "__main__":
    main()
