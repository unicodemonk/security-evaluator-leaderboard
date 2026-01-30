"""
Validator Agent - Attack validation.

Validates attacks for syntax correctness, semantic validity, and realism.
"""

from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime

from ..base import UnifiedAgent, AgentCapabilities, Capability, AgentRole, Task, KnowledgeBase, Validator
from ..models import Attack


class ValidatorAgent(UnifiedAgent):
    """
    Agent that validates attacks before testing.

    Ensures attacks are valid and well-formed.
    """

    def __init__(
        self,
        agent_id: str,
        knowledge_base: KnowledgeBase,
        validators: List[Validator],
        llm_client: Optional[Any] = None,
        model_router: Optional[Any] = None,
        use_llm_semantic_check: bool = True
    ):
        """
        Initialize validator agent.

        Args:
            agent_id: Unique agent identifier
            knowledge_base: Shared knowledge base
            validators: List of validators to apply
            llm_client: Optional LLM client for semantic validation
            model_router: Optional model router for cost optimization
            use_llm_semantic_check: Whether to use LLM for semantic validation
        """
        capabilities = AgentCapabilities(
            capabilities={Capability.VALIDATE},
            role=AgentRole.VALIDATOR,
            requires_llm=llm_client is not None,
            cost_per_invocation=0.03 if llm_client else 0.0,
            avg_latency_ms=1000.0 if llm_client else 50.0
        )
        super().__init__(agent_id, capabilities, knowledge_base)
        self.validators = validators
        self.llm_client = llm_client
        self.model_router = model_router
        self.use_llm_semantic_check = use_llm_semantic_check

        # Validation statistics
        self.total_validated = 0
        self.total_valid = 0
        self.total_invalid = 0
        self.invalid_by_type: Dict[str, int] = {}

    def execute_task(self, task: Task) -> Any:
        """
        Execute validation task.

        Args:
            task: Task with parameters:
                - attacks: List of attacks to validate

        Returns:
            Dictionary with validation results
        """
        attacks = task.parameters.get('attacks', [])

        if not attacks:
            self.logger.warning("No attacks to validate")
            return {'valid': [], 'invalid': []}

        # Validate attacks
        valid_attacks = []
        invalid_attacks = []

        for attack in attacks:
            is_valid, error_msg = self._validate_attack(attack)

            if is_valid:
                # Only set attributes if attack is an Attack object (not a string)
                if hasattr(attack, 'is_valid'):
                    attack.is_valid = True
                valid_attacks.append(attack)
                self.total_valid += 1
            else:
                # Only set attributes if attack is an Attack object (not a string)
                if hasattr(attack, 'is_valid'):
                    attack.is_valid = False
                if hasattr(attack, 'validation_errors'):
                    attack.validation_errors.append(error_msg)
                invalid_attacks.append(attack)
                self.total_invalid += 1

            self.total_validated += 1

        # Share knowledge
        self.share_knowledge(
            entry_type='validation',
            data={
                'total_validated': len(attacks),
                'num_valid': len(valid_attacks),
                'num_invalid': len(invalid_attacks),
                'invalid_by_type': self.invalid_by_type
            },
            tags={'validation'}
        )

        return {
            'valid': valid_attacks,
            'invalid': invalid_attacks,
            'validation_rate': len(valid_attacks) / len(attacks) if attacks else 0.0
        }

    def _validate_attack(self, attack: Attack) -> Tuple[bool, Optional[str]]:
        """
        Validate an attack using algorithmic validators + optional LLM semantic check.

        Args:
            attack: Attack to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Step 1: Algorithmic validation (syntax, structure)
        for validator in self.validators:
            is_valid, error_msg = validator.validate(attack)

            if not is_valid:
                # Track validation failure by type
                validator_type = validator.get_validator_type()
                self.invalid_by_type[validator_type] = self.invalid_by_type.get(validator_type, 0) + 1

                return False, f"{validator_type}: {error_msg}"

        # Step 2: LLM semantic validation (realism, executability)
        if self.llm_client and self.use_llm_semantic_check:
            is_valid, error_msg = self._llm_semantic_validate(attack)
            if not is_valid:
                self.invalid_by_type['llm_semantic'] = self.invalid_by_type.get('llm_semantic', 0) + 1
                return False, f"llm_semantic: {error_msg}"

        return True, None

    def _llm_semantic_validate(self, attack: Attack) -> Tuple[bool, Optional[str]]:
        """
        LLM-based semantic validation.

        Checks if attack is realistic, executable, and makes sense semantically.

        Args:
            attack: Attack to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Get category from metadata if available
        category = attack.metadata.get('category', 'Unknown') if attack.metadata else 'Unknown'

        prompt = f"""You are a security expert validating attack test cases.

Attack Payload:
{attack.payload}

Technique: {attack.technique}
Category: {category}

Validate this attack for:
1. **Realism**: Could this attack realistically be attempted?
2. **Executability**: Is the payload syntactically valid for its technique?
3. **Semantic Correctness**: Does the payload make semantic sense?
4. **Not Trivially Broken**: Is it not obviously malformed or nonsensical?

Answer in this format:
VALID: YES or NO
REASON: <brief explanation if NO>
"""

        try:
            # Route to appropriate model if router available
            if self.model_router:
                task = Task(
                    task_id=f"validate_{attack.attack_id}_{datetime.now().timestamp()}",
                    task_type='validate',
                    description=f"Semantic validation",
                    parameters={'attack_id': attack.attack_id}
                )
                model_client = self.model_router.route(task, prompt)
                self.logger.info(f"Routed to model: {model_client.name}")
            else:
                model_client = self.llm_client

            response = model_client.generate(
                prompt=prompt,
                max_tokens=150,
                temperature=0.3  # Low temperature for consistent validation
            )

            # Parse response - handle both string and object responses
            if isinstance(response, str):
                response_content = response
            elif hasattr(response, 'content'):
                response_content = response.content
            else:
                response_content = str(response)

            response_text = response_content.upper()

            if 'VALID: YES' in response_text:
                is_valid = True
                error_msg = None
            elif 'VALID: NO' in response_text:
                is_valid = False
                # Extract reason
                lines = response_content.split('\n')
                error_msg = "LLM validation failed"
                for line in lines:
                    if line.startswith('REASON:'):
                        error_msg = line.split(':', 1)[1].strip()
                        break
            else:
                # Ambiguous response, default to valid to avoid false negatives
                self.logger.warning(f"Ambiguous LLM validation response: {response_content[:100]}")
                is_valid = True
                error_msg = None

            # Update router with quality feedback
            if self.model_router:
                # Quality: response should contain VALID: YES or VALID: NO
                has_verdict = 'VALID:' in response_text
                quality_feedback = 1.0 if has_verdict else 0.3
                self.model_router.update('validate', quality_feedback)

            self.logger.info(f"LLM validation: {attack.attack_id} -> {'VALID' if is_valid else 'INVALID'}")
            return is_valid, error_msg

        except Exception as e:
            self.logger.error(f"LLM validation failed: {e}")
            # Default to valid on error to avoid false negatives
            return True, None

    def can_execute(self, task: Task) -> bool:
        """Check if agent can execute task."""
        return task.task_type in ['validate', 'check_validity']

    def get_validation_stats(self) -> Dict[str, Any]:
        """
        Get validation statistics.

        Returns:
            Dictionary with validation stats
        """
        return {
            'total_validated': self.total_validated,
            'total_valid': self.total_valid,
            'total_invalid': self.total_invalid,
            'validation_rate': self.total_valid / self.total_validated if self.total_validated > 0 else 0.0,
            'invalid_by_type': self.invalid_by_type.copy()
        }
