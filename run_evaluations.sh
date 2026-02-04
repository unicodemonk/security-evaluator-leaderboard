#!/bin/bash

# Agent IDs
LAW_PURPLE_ID="019bc3e1-463c-7712-b376-7e71ccdcdaa3"
HOME_AUTO_ID="019b949b-4b3e-7800-bf9d-73966e9aec2d"

# Function to update scenario.toml and trigger evaluation
run_evaluation() {
    local agent_id=$1
    local agent_name=$2
    
    echo "=== Evaluating $agent_name ($agent_id) ==="
    
    # Update scenario.toml
    sed -i.bak "s/agentbeats_id = \"[^\"]*\"/agentbeats_id = \"$agent_id\"/" scenario.toml
    
    # Commit and push
    git add scenario.toml
    git commit -m "Update scenario.toml for $agent_name evaluation"
    git push origin main
    
    echo "Waiting for evaluation to complete..."
    sleep 30
    
    # Wait for the workflow to start
    for i in {1..10}; do
        RUN_ID=$(gh run list --limit 1 --json databaseId,status --jq '.[0] | select(.status == "in_progress" or .status == "queued") | .databaseId')
        if [ -n "$RUN_ID" ]; then
            echo "Workflow started (ID: $RUN_ID)"
            break
        fi
        sleep 5
    done
    
    if [ -n "$RUN_ID" ]; then
        gh run watch $RUN_ID
    else
        echo "Warning: Could not find running workflow"
    fi
    
    echo ""
}

# Run evaluations
run_evaluation "$LAW_PURPLE_ID" "law-purple-agent"
run_evaluation "$HOME_AUTO_ID" "home-automation-agent"

echo "=== All evaluations complete ==="
