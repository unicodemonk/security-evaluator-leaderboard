"""
Perspective Agent - Multi-perspective assessment.

Provides quality assessments from different viewpoints (security expert, developer, pentester).
"""

from typing import Any, Dict, List, Optional
from datetime import datetime

from ..base import UnifiedAgent, AgentCapabilities, Capability, AgentRole, Task, KnowledgeBase
from ..models import PerspectiveAssessment


class PerspectiveAgent(UnifiedAgent):
    """
    Agent that provides quality assessment from a specific perspective.

    Requires LLM for expert viewpoint simulation.
    """

    def __init__(
        self,
        agent_id: str,
        knowledge_base: KnowledgeBase,
        perspective_type: str,  # 'security_expert', 'developer', 'pentester'
        llm_client: Any,
        model_router: Optional[Any] = None
    ):
        """
        Initialize perspective agent.

        Args:
            agent_id: Unique agent identifier
            knowledge_base: Shared knowledge base
            perspective_type: Type of perspective
            llm_client: LLM client for assessments
            model_router: Optional model router for cost optimization
        """
        capabilities = AgentCapabilities(
            capabilities={Capability.EVALUATE},
            role=AgentRole.PERSPECTIVE,
            requires_llm=True,
            cost_per_invocation=0.10,
            avg_latency_ms=2000.0
        )
        super().__init__(agent_id, capabilities, knowledge_base)
        self.perspective_type = perspective_type
        self.llm_client = llm_client
        self.model_router = model_router

        # Assessment history
        self.assessments: List[PerspectiveAssessment] = []

    def execute_task(self, task: Task) -> Any:
        """
        Execute perspective assessment task.

        Args:
            task: Task with parameters:
                - evaluation_result: Evaluation result to assess

        Returns:
            Perspective assessment
        """
        evaluation_result = task.parameters.get('evaluation_result')

        if not evaluation_result:
            self.logger.error("Missing evaluation_result")
            return {'error': 'Missing evaluation_result'}

        # Generate assessment
        assessment = self._assess_evaluation(evaluation_result)
        self.assessments.append(assessment)

        # Share knowledge
        self.share_knowledge(
            entry_type='perspective',
            data={
                'perspective_type': self.perspective_type,
                'quality_score': assessment.quality_score,
                'num_concerns': len(assessment.concerns),
                'num_recommendations': len(assessment.recommendations)
            },
            tags={'perspective', self.perspective_type}
        )

        return {'assessment': assessment}

    def _assess_evaluation(self, evaluation_result: Any) -> PerspectiveAssessment:
        """
        Generate perspective assessment.

        Args:
            evaluation_result: Evaluation result

        Returns:
            Perspective assessment
        """
        # Build prompt for LLM
        prompt = self._build_assessment_prompt(evaluation_result)

        # Call LLM with smart routing
        try:
            # Route to appropriate model if router available
            if self.model_router:
                task = Task(
                    task_id=f"assess_{self.perspective_type}_{datetime.now().timestamp()}",
                    task_type='assess',
                    description=f"Assess evaluation from {self.perspective_type} perspective",
                    parameters={'perspective_type': self.perspective_type}
                )
                model_client = self.model_router.route(task, prompt)
                self.logger.info(f"Routed to model: {model_client.name}")
            else:
                model_client = self.llm_client

            response = model_client.generate(
                prompt=prompt,
                max_tokens=1000,
                temperature=0.7
            )

            # Parse response
            quality_score, comments, concerns, recommendations = self._parse_assessment(response)

            # Update router with quality feedback
            if self.model_router:
                # Assess quality based on how well the response was parsed
                has_concerns = len(concerns) > 0
                has_recommendations = len(recommendations) > 0
                quality_feedback = 1.0 if (has_concerns and has_recommendations) else 0.5
                self.model_router.update('assess', quality_feedback)

        except Exception as e:
            self.logger.error(f"LLM assessment failed: {e}")
            quality_score = 0.5
            comments = f"Assessment failed: {e}"
            concerns = ["LLM call failed"]
            recommendations = []

        # Create assessment
        assessment = PerspectiveAssessment(
            perspective_id=f"{self.agent_id}_{datetime.now().timestamp()}",
            perspective_type=self.perspective_type,
            agent_id=self.agent_id,
            quality_score=quality_score,
            comments=comments,
            concerns=concerns,
            recommendations=recommendations,
            llm_model=model_client.model_name if hasattr(model_client, 'model_name') else 'unknown',
            cost_usd=0.10  # Approximate
        )

        return assessment

    def _build_assessment_prompt(self, evaluation_result: Any) -> str:
        """Build assessment prompt."""
        prompt = f"""You are a {self.perspective_type} reviewing a security evaluation.

Evaluation Summary:
- Purple Agent: {evaluation_result.purple_agent}
- Scenario: {evaluation_result.scenario}
- Total Attacks Tested: {evaluation_result.total_attacks_tested}
- Metrics:
  * Precision: {evaluation_result.metrics.precision:.3f}
  * Recall: {evaluation_result.metrics.recall:.3f}
  * F1 Score: {evaluation_result.metrics.f1_score:.3f}
  * False Negative Rate: {evaluation_result.metrics.false_negative_rate:.3f}

Evasions Found: {len(evaluation_result.get_evasions())}

As a {self.perspective_type}, assess this evaluation:
1. Quality Score (0.0-1.0): How thorough and valid is this evaluation?
2. Comments: Your overall assessment
3. Concerns: List 2-4 specific concerns
4. Recommendations: List 2-4 recommendations

Format your response as:
SCORE: <0.0-1.0>
COMMENTS: <your comments>
CONCERNS:
- <concern 1>
- <concern 2>
RECOMMENDATIONS:
- <recommendation 1>
- <recommendation 2>
"""
        return prompt

    def _parse_assessment(self, response: str) -> tuple:
        """
        Parse LLM assessment response.

        Returns:
            Tuple of (quality_score, comments, concerns, recommendations)
        """
        lines = response.strip().split('\n')

        quality_score = 0.5
        comments = ""
        concerns = []
        recommendations = []

        current_section = None

        for line in lines:
            line = line.strip()

            if line.startswith('SCORE:'):
                try:
                    quality_score = float(line.split(':', 1)[1].strip())
                except:
                    quality_score = 0.5

            elif line.startswith('COMMENTS:'):
                comments = line.split(':', 1)[1].strip()

            elif line.startswith('CONCERNS:'):
                current_section = 'concerns'

            elif line.startswith('RECOMMENDATIONS:'):
                current_section = 'recommendations'

            elif line.startswith('-'):
                item = line[1:].strip()
                if current_section == 'concerns':
                    concerns.append(item)
                elif current_section == 'recommendations':
                    recommendations.append(item)

        return quality_score, comments, concerns, recommendations

    def can_execute(self, task: Task) -> bool:
        """Check if agent can execute task."""
        return task.task_type in ['assess', 'evaluate_quality']
