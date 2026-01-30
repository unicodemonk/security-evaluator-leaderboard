"""
Counterfactual Agent - Failure analysis.

Implements counterfactual failure analysis (Enhancement 4) using beam search
to find minimal edits that would make an evasion detectable.
"""

from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime
import copy

from ..base import UnifiedAgent, AgentCapabilities, Capability, AgentRole, Task, KnowledgeBase, PurpleAgent
from ..models import Attack, TestResult, CounterfactualResult


class CounterfactualAgent(UnifiedAgent):
    """
    Agent that analyzes failures to find minimal remediations.

    Uses beam search to find smallest edits that would prevent evasion.
    """

    def __init__(
        self,
        agent_id: str,
        knowledge_base: KnowledgeBase,
        scenario: 'SecurityScenario',
        beam_width: int = 5,
        max_depth: int = 3,
        llm_client: Optional[Any] = None,
        model_router: Optional[Any] = None,
        use_llm_suggestions: bool = True
    ):
        """
        Initialize counterfactual agent.

        Args:
            agent_id: Unique agent identifier
            knowledge_base: Shared knowledge base
            scenario: Security scenario
            beam_width: Beam search width
            max_depth: Maximum edit depth
            llm_client: Optional LLM client for smart remediation suggestions
            model_router: Optional model router for cost optimization
            use_llm_suggestions: Whether to use LLM for remediation suggestions
        """
        capabilities = AgentCapabilities(
            capabilities={Capability.EVALUATE},
            role=AgentRole.COUNTERFACTUAL_ANALYZER,
            requires_llm=llm_client is not None,
            cost_per_invocation=0.08 if llm_client else 0.0,
            avg_latency_ms=2000.0 if llm_client else 500.0
        )
        super().__init__(agent_id, capabilities, knowledge_base)
        self.scenario = scenario
        self.beam_width = beam_width
        self.max_depth = max_depth
        self.llm_client = llm_client
        self.model_router = model_router
        self.use_llm_suggestions = use_llm_suggestions

        # Analysis results
        self.counterfactual_results: List[CounterfactualResult] = []

    def execute_task(self, task: Task) -> Any:
        """
        Execute counterfactual analysis task.

        Args:
            task: Task with parameters:
                - evasions: List of evasion attacks (False Negatives)
                - purple_agent: Target agent

        Returns:
            List of counterfactual results
        """
        evasions = task.parameters.get('evasions', [])
        purple_agent = task.parameters.get('purple_agent')

        if not evasions or not purple_agent:
            self.logger.error("Missing evasions or purple_agent")
            return {'error': 'Missing data'}

        # Analyze each evasion
        results = []
        for evasion in evasions:
            result = self._analyze_evasion(evasion, purple_agent)
            if result:
                results.append(result)
                self.counterfactual_results.append(result)

        # Share knowledge
        self.share_knowledge(
            entry_type='counterfactual',
            data={
                'num_analyzed': len(evasions),
                'num_successful': len(results),
                'avg_edit_distance': sum(r.edit_distance for r in results) / len(results) if results else 0
            },
            tags={'counterfactual', 'remediation'}
        )

        return {'counterfactual_results': results}

    def _analyze_evasion(
        self,
        evasion_attack: Attack,
        purple_agent: PurpleAgent
    ) -> Optional[CounterfactualResult]:
        """
        Find minimal edits to make evasion detectable using hybrid LLM + beam search.

        Args:
            evasion_attack: Attack that evaded detection
            purple_agent: Target agent

        Returns:
            Counterfactual result with minimal edits
        """
        self.logger.info(f"Analyzing evasion {evasion_attack.attack_id}")

        # Use LLM for smart suggestions if available
        if self.llm_client and self.use_llm_suggestions:
            llm_result = self._llm_suggest_remediation(evasion_attack, purple_agent)
            if llm_result:
                return llm_result

        # Fall back to beam search
        return self._beam_search_remediation(evasion_attack, purple_agent)

    def _beam_search_remediation(
        self,
        evasion_attack: Attack,
        purple_agent: PurpleAgent
    ) -> Optional[CounterfactualResult]:
        """
        Beam search approach to find minimal edits.

        Args:
            evasion_attack: Attack that evaded detection
            purple_agent: Target agent

        Returns:
            Counterfactual result with minimal edits
        """

        # Beam search for minimal edits
        beam = [(evasion_attack, [], 0)]  # (attack, edits, depth)
        best_counterfactual = None

        for depth in range(self.max_depth):
            candidates = []

            for attack, edits, d in beam:
                if d != depth:
                    continue

                # Generate edit candidates
                new_candidates = self._generate_edit_candidates(attack)

                for new_attack, edit in new_candidates:
                    # Test if now detected
                    result = self.scenario.execute_attack(new_attack, purple_agent)

                    if result.detected:
                        # Found a counterfactual!
                        new_edits = edits + [edit]

                        # Check if this is better than current best
                        if not best_counterfactual or len(new_edits) < best_counterfactual.edit_distance:
                            best_counterfactual = CounterfactualResult(
                                attack_id=evasion_attack.attack_id,
                                original_payload=evasion_attack.payload,
                                counterfactual_payload=new_attack.payload,
                                edit_distance=len(new_edits),
                                edits=new_edits,
                                now_detected=True,
                                explanation=self._generate_explanation(evasion_attack, new_attack, new_edits),
                                confidence=result.confidence
                            )
                    else:
                        # Not detected yet, continue search
                        candidates.append((new_attack, edits + [edit], depth + 1))

            # Keep top beam_width candidates
            candidates.sort(key=lambda x: len(x[1]))  # Sort by edit count
            beam = candidates[:self.beam_width]

            # Early termination if found good solution
            if best_counterfactual and best_counterfactual.edit_distance <= 1:
                break

        return best_counterfactual

    def _llm_suggest_remediation(
        self,
        evasion_attack: Attack,
        purple_agent: PurpleAgent
    ) -> Optional[CounterfactualResult]:
        """
        Use LLM to suggest minimal remediation for evasion.

        Args:
            evasion_attack: Attack that evaded detection
            purple_agent: Target agent

        Returns:
            Counterfactual result with LLM-suggested remediation
        """
        prompt = f"""You are a security expert analyzing why an attack evaded detection.

Attack that EVADED detection:
Payload: {evasion_attack.payload}
Technique: {evasion_attack.technique}

Scenario: {self.scenario.name}

Your task:
1. Identify WHY this attack evaded detection (obfuscation, encoding, etc.)
2. Suggest the MINIMAL change to make it detectable
3. Provide a remediation recommendation for the detector

Respond in this format:
EVASION_REASON: <why it evaded>
MINIMAL_FIX: <the smallest change to make it detectable>
REMEDIATION: <recommendation for improving the detector>
"""

        try:
            # Route to appropriate model if router available
            if self.model_router:
                task = Task(
                    task_id=f"remediate_{evasion_attack.attack_id}_{datetime.now().timestamp()}",
                    task_type='counterfactual',
                    description=f"Suggest remediation",
                    parameters={'attack_id': evasion_attack.attack_id}
                )
                model_client = self.model_router.route(task, prompt)
                self.logger.info(f"Routed to model: {model_client.name}")
            else:
                model_client = self.llm_client

            response = model_client.generate(
                prompt=prompt,
                max_tokens=400,
                temperature=0.5  # Moderate temperature for creative but focused suggestions
            )

            # Parse response
            lines = response.content.split('\n')
            evasion_reason = ""
            minimal_fix = ""
            remediation = ""

            for line in lines:
                if line.startswith('EVASION_REASON:'):
                    evasion_reason = line.split(':', 1)[1].strip()
                elif line.startswith('MINIMAL_FIX:'):
                    minimal_fix = line.split(':', 1)[1].strip()
                elif line.startswith('REMEDIATION:'):
                    remediation = line.split(':', 1)[1].strip()

            if not minimal_fix:
                self.logger.warning(f"LLM didn't provide minimal fix, using beam search")
                return None

            # Create suggested counterfactual payload
            counterfactual_payload = minimal_fix

            # Test if the suggestion works
            test_attack = self.scenario.create_attack(
                technique=evasion_attack.technique,
                payload=counterfactual_payload,
                metadata={'source': 'llm_remediation'}
            )

            result = self.scenario.execute_attack(test_attack, purple_agent)

            if result.detected:
                # LLM suggestion worked!
                explanation = f"""LLM Analysis:
Evasion Reason: {evasion_reason}

Minimal Fix: {minimal_fix}

Remediation Recommendation: {remediation}

Original Payload: {evasion_attack.payload}
Suggested Payload (would be detected): {counterfactual_payload}
"""

                counterfactual_result = CounterfactualResult(
                    attack_id=evasion_attack.attack_id,
                    original_payload=evasion_attack.payload,
                    counterfactual_payload=counterfactual_payload,
                    edit_distance=1,  # LLM provides conceptual edits
                    edits=[{'type': 'llm_suggestion', 'description': minimal_fix}],
                    now_detected=True,
                    explanation=explanation,
                    confidence=result.confidence
                )

                # Update router with quality feedback
                if self.model_router:
                    # High quality if suggestion led to detection
                    quality_feedback = 1.0
                    self.model_router.update('counterfactual', quality_feedback)

                self.logger.info(f"LLM remediation successful: {evasion_attack.attack_id}")
                return counterfactual_result
            else:
                self.logger.warning(f"LLM suggestion didn't result in detection")
                # Update router with low quality feedback
                if self.model_router:
                    self.model_router.update('counterfactual', 0.3)
                return None

        except Exception as e:
            self.logger.error(f"LLM remediation failed: {e}")
            return None

    def _generate_edit_candidates(self, attack: Attack) -> List[Tuple[Attack, Dict[str, Any]]]:
        """
        Generate edit candidates for an attack.

        Args:
            attack: Base attack

        Returns:
            List of (edited_attack, edit_description) tuples
        """
        candidates = []

        payload_str = str(attack.payload)

        # Edit type 1: Character removal
        for i in range(len(payload_str)):
            if i > 0:  # Don't remove first character
                edited_payload = payload_str[:i] + payload_str[i+1:]
                edited_attack = self.scenario.create_attack(
                    technique=attack.technique,
                    payload=edited_payload,
                    metadata={'edit_type': 'removal', 'position': i}
                )
                edit_desc = {'type': 'remove_char', 'position': i, 'char': payload_str[i]}
                candidates.append((edited_attack, edit_desc))

        # Edit type 2: Character addition (common security chars)
        security_chars = ['\'', '"', ';', '(', ')', '--', '#']
        for i in range(min(5, len(payload_str))):  # Limit to first 5 positions
            for char in security_chars:
                edited_payload = payload_str[:i] + char + payload_str[i:]
                edited_attack = self.scenario.create_attack(
                    technique=attack.technique,
                    payload=edited_payload,
                    metadata={'edit_type': 'addition', 'position': i}
                )
                edit_desc = {'type': 'add_char', 'position': i, 'char': char}
                candidates.append((edited_attack, edit_desc))

        # Edit type 3: Substring removal (remove obfuscation)
        common_obfuscations = ['/*', '*/', '%20', '%00', 'null']
        for obf in common_obfuscations:
            if obf in payload_str:
                edited_payload = payload_str.replace(obf, '', 1)
                edited_attack = self.scenario.create_attack(
                    technique=attack.technique,
                    payload=edited_payload,
                    metadata={'edit_type': 'deobfuscation'}
                )
                edit_desc = {'type': 'remove_obfuscation', 'removed': obf}
                candidates.append((edited_attack, edit_desc))

        return candidates

    def _generate_explanation(
        self,
        original: Attack,
        counterfactual: Attack,
        edits: List[Dict[str, Any]]
    ) -> str:
        """
        Generate human-readable explanation.

        Args:
            original: Original evasion
            counterfactual: Counterfactual that would be detected
            edits: List of edits made

        Returns:
            Explanation string
        """
        explanation = f"The attack evaded detection with payload: {original.payload}\n\n"
        explanation += f"Minimal edits to make it detectable ({len(edits)} edits):\n"

        for i, edit in enumerate(edits, 1):
            if edit['type'] == 'remove_char':
                explanation += f"{i}. Remove character '{edit['char']}' at position {edit['position']}\n"
            elif edit['type'] == 'add_char':
                explanation += f"{i}. Add character '{edit['char']}' at position {edit['position']}\n"
            elif edit['type'] == 'remove_obfuscation':
                explanation += f"{i}. Remove obfuscation pattern '{edit['removed']}'\n"

        explanation += f"\nResulting payload would be: {counterfactual.payload}\n"
        explanation += "\nRecommendation: Update detection rules to catch patterns similar to the original payload."

        return explanation

    def can_execute(self, task: Task) -> bool:
        """Check if agent can execute task."""
        return task.task_type in ['counterfactual', 'analyze_failure']

    def get_analysis_stats(self) -> Dict[str, Any]:
        """
        Get analysis statistics.

        Returns:
            Dictionary with stats
        """
        if not self.counterfactual_results:
            return {'num_analyzed': 0}

        return {
            'num_analyzed': len(self.counterfactual_results),
            'avg_edit_distance': sum(r.edit_distance for r in self.counterfactual_results) / len(self.counterfactual_results),
            'min_edit_distance': min(r.edit_distance for r in self.counterfactual_results),
            'max_edit_distance': max(r.edit_distance for r in self.counterfactual_results)
        }
