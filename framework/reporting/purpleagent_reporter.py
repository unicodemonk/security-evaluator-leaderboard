"""
Purple Agent Reporter.

Generates security posture assessment reports for Purple Agents.
Focuses on vulnerabilities, CVSS scores, risk levels, and remediation guidance.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime

from framework.models import PurpleAgentAssessment, DualEvaluationResult, Vulnerability


class PurpleAgentReporter:
    """
    Generates Purple Agent security posture assessment reports.
    
    Produces reports focused on:
    - Security vulnerabilities and CVSS scores
    - Risk levels and security posture grades
    - Remediation priorities and timelines
    - Compliance and recommendations
    
    Audience: Defenders, Security teams, Management, Compliance
    """

    def __init__(self):
        """Initialize Purple Agent reporter."""
        pass

    def generate_markdown_report(
        self,
        dual_result: DualEvaluationResult,
        include_all_vulnerabilities: bool = False,
        top_n_vulnerabilities: int = 10
    ) -> str:
        """
        Generate markdown format security assessment report.

        Args:
            dual_result: Dual evaluation result
            include_all_vulnerabilities: Whether to include all vulnerabilities
            top_n_vulnerabilities: Number of top vulnerabilities to show

        Returns:
            Markdown formatted security report
        """
        assessment = dual_result.purple_agent_assessment
        
        report = []
        report.append(f"# Security Posture Assessment Report: {assessment.purple_agent_name}\n\n")
        report.append(f"**Evaluation ID:** `{dual_result.evaluation_id}`\n")
        report.append(f"**Assessment Date:** {assessment.assessment_date.strftime('%Y-%m-%d %H:%M:%S')}\n")
        report.append(f"**Scenario:** {dual_result.scenario}\n")
        report.append(f"**Duration:** {dual_result.total_time_seconds:.1f} seconds\n\n")
        
        report.append("---\n\n")
        
        # Executive Summary
        report.append("## 🛡️ Executive Summary\n\n")
        report.append(f"**Security Score:** {assessment.security_score:.1f}/100 ({assessment.security_grade})\n\n")
        report.append(f"**Risk Level:** 🔴 **{assessment.risk_level}**\n\n")
        report.append(self._get_security_status(assessment))
        report.append("\n\n---\n\n")
        
        # Vulnerability Summary
        report.append("## 🚨 Vulnerability Summary\n\n")
        report.append(f"**Total Vulnerabilities Found:** {assessment.total_vulnerabilities}\n\n")
        
        if assessment.total_vulnerabilities > 0:
            report.append("### By Severity\n\n")
            report.append("```\n")
            if assessment.critical_count > 0:
                report.append(f"Critical (9.0-10.0):  {'█' * min(assessment.critical_count, 40)} {assessment.critical_count}\n")
            if assessment.high_count > 0:
                report.append(f"High     (7.0-8.9):   {'█' * min(assessment.high_count, 40)} {assessment.high_count}\n")
            if assessment.medium_count > 0:
                report.append(f"Medium   (4.0-6.9):   {'█' * min(assessment.medium_count, 40)} {assessment.medium_count}\n")
            if assessment.low_count > 0:
                report.append(f"Low      (0.1-3.9):   {'█' * min(assessment.low_count, 40)} {assessment.low_count}\n")
            report.append("```\n\n")
            
            report.append(f"- **Average CVSS Score:** {assessment.average_cvss_score:.1f}\n")
            report.append(f"- **Maximum CVSS Score:** {assessment.max_cvss_score:.1f}\n\n")
        
        # Security Metrics
        report.append("### Security Metrics\n\n")
        report.append("| Metric | Value | Status |\n")
        report.append("|--------|-------|--------|\n")
        report.append(f"| **Attack Success Rate** | {assessment.attack_success_rate:.1f}% | {self._get_status_icon(assessment.attack_success_rate, inverse=True)} |\n")
        report.append(f"| **Defense Success Rate** | {assessment.defense_success_rate:.1f}% | {self._get_status_icon(assessment.defense_success_rate)} |\n")
        report.append(f"| **Total Tests** | {assessment.total_tests} | ℹ️ |\n\n")
        
        report.append("---\n\n")
        
        # MITRE Technique Coverage
        mitre_techniques = {}
        atlas_count = 0
        attack_count = 0
        
        for vuln in assessment.vulnerabilities:
            mitre_id = vuln.metadata.get('mitre_technique_id')
            if mitre_id:
                mitre_name = vuln.metadata.get('mitre_technique_name', 'Unknown')
                if mitre_id not in mitre_techniques:
                    mitre_techniques[mitre_id] = {
                        'name': mitre_name,
                        'count': 0,
                        'is_atlas': mitre_id.startswith('AML.')
                    }
                mitre_techniques[mitre_id]['count'] += 1
                
                if mitre_id.startswith('AML.'):
                    atlas_count += 1
                else:
                    attack_count += 1
        
        if mitre_techniques:
            report.append("## 🎯 MITRE Technique Coverage\n\n")
            report.append(f"**Total MITRE Techniques Used:** {len(mitre_techniques)}\n")
            report.append(f"- ATLAS (AI/ML Security): {len([t for t in mitre_techniques.values() if t['is_atlas']])} techniques\n")
            report.append(f"- ATT&CK (General): {len([t for t in mitre_techniques.values() if not t['is_atlas']])} techniques\n\n")
            
            report.append(f"**Total Vulnerabilities by Source:**\n")
            if atlas_count > 0:
                report.append(f"- ATLAS: {atlas_count} vulnerabilities\n")
            if attack_count > 0:
                report.append(f"- ATT&CK: {attack_count} vulnerabilities\n")
            report.append("\n")
            
            # List top techniques
            sorted_techniques = sorted(mitre_techniques.items(), key=lambda x: x[1]['count'], reverse=True)
            report.append("### Top MITRE Techniques Used\n\n")
            report.append("| Technique ID | Technique Name | Vulnerabilities | Type |\n")
            report.append("|--------------|----------------|-----------------|------|\n")
            for tech_id, tech_info in sorted_techniques[:10]:
                tech_type = "ATLAS" if tech_info['is_atlas'] else "ATT&CK"
                report.append(f"| {tech_id} | {tech_info['name'][:50]} | {tech_info['count']} | {tech_type} |\n")
            report.append("\n")
            report.append("---\n\n")
        
        # Top Vulnerabilities
        if assessment.vulnerabilities:
            report.append(f"## 🔍 Top {min(top_n_vulnerabilities, len(assessment.vulnerabilities))} Critical Vulnerabilities\n\n")
            
            sorted_vulns = sorted(assessment.vulnerabilities, key=lambda v: v.cvss_score, reverse=True)
            for i, vuln in enumerate(sorted_vulns[:top_n_vulnerabilities], 1):
                report.append(f"### {i}. {vuln.vulnerability_id}: {vuln.cwe_name}\n\n")
                
                # MITRE Technique Information (if available)
                mitre_id = vuln.metadata.get('mitre_technique_id')
                mitre_name = vuln.metadata.get('mitre_technique_name')
                if mitre_id:
                    # Determine if ATLAS or ATT&CK based on ID format
                    if mitre_id.startswith('AML.'):
                        mitre_url = f"https://atlas.mitre.org/techniques/{mitre_id}"
                        mitre_type = "ATLAS (AI/ML)"
                    else:
                        mitre_url = f"https://attack.mitre.org/techniques/{mitre_id.replace('.', '/')}"
                        mitre_type = "ATT&CK"
                    report.append(f"**MITRE {mitre_type}:** [{mitre_id}]({mitre_url}) - {mitre_name}\n\n")
                    
                    # Full MITRE Details
                    mitre_tactics = vuln.metadata.get('mitre_tactics', [])
                    mitre_platforms = vuln.metadata.get('mitre_platforms', [])
                    mitre_source = vuln.metadata.get('mitre_source', 'unknown')
                    
                    if mitre_tactics or mitre_platforms:
                        report.append("**MITRE Technique Details:**\n")
                        if mitre_tactics:
                            tactics_str = ", ".join(mitre_tactics)
                            report.append(f"- **Tactics:** {tactics_str}\n")
                        if mitre_platforms:
                            platforms_str = ", ".join(mitre_platforms)
                            report.append(f"- **Platforms:** {platforms_str}\n")
                        report.append(f"- **Source:** {mitre_source}\n\n")
                
                report.append(f"**CVSS Score:** {vuln.cvss_score:.1f} ({vuln.severity})\n\n")
                report.append(f"**CWE:** [{vuln.cwe_id}](https://cwe.mitre.org/data/definitions/{vuln.cwe_id.replace('CWE-', '')}.html) - {vuln.cwe_name}\n\n")
                
                # Additional Attack Details
                mitre_category = vuln.metadata.get('mitre_category') or vuln.metadata.get('category')
                mitre_platform = vuln.metadata.get('mitre_platform') or vuln.metadata.get('platform')
                generation_source = vuln.metadata.get('generation_source')
                
                if mitre_category or mitre_platform or generation_source:
                    report.append("**Attack Details:**\n")
                    if mitre_category:
                        report.append(f"- Category: {mitre_category}\n")
                    if mitre_platform:
                        report.append(f"- Platform: {mitre_platform}\n")
                    if generation_source:
                        report.append(f"- Generation Source: {generation_source}\n")
                    report.append("\n")
                
                report.append(f"**Description:**\n{vuln.description}\n\n")
                
                # Enhanced Proof of Concept with structured sections
                report.append("**Proof of Concept:**\n\n")
                
                # Extract payload from proof_of_concept or metadata
                payload = None
                agent_response = None
                
                # Try to extract from metadata first (more reliable)
                if 'attack_payload' in vuln.metadata:
                    payload = vuln.metadata['attack_payload']
                elif 'payload' in vuln.metadata:
                    payload = vuln.metadata['payload']
                else:
                    # Parse from proof_of_concept string
                    poc_lines = vuln.proof_of_concept.split('\n')
                    for line in poc_lines:
                        if line.startswith('Payload:'):
                            payload = line.replace('Payload:', '').strip()
                            if payload.endswith('... [truncated]'):
                                payload = payload.replace('... [truncated]', '')
                
                # Extract agent response - check multiple possible keys
                agent_response = None
                if 'agent_response' in vuln.metadata and vuln.metadata['agent_response']:
                    agent_response = vuln.metadata['agent_response']
                elif 'purple_agent_response' in vuln.metadata and vuln.metadata['purple_agent_response']:
                    agent_response = vuln.metadata['purple_agent_response']
                elif 'response' in vuln.metadata and vuln.metadata['response']:
                    agent_response = vuln.metadata['response']
                else:
                    # Parse from proof_of_concept as fallback
                    poc_lines = vuln.proof_of_concept.split('\n')
                    for line in poc_lines:
                        if 'Purple Agent Response:' in line or 'Response:' in line:
                            agent_response = line.split(':', 1)[1].strip() if ':' in line else None
                            if agent_response and agent_response.endswith('... [truncated]'):
                                agent_response = agent_response.replace('... [truncated]', '')
                            break
                
                # Convert dict response to formatted string if needed
                if agent_response:
                    if isinstance(agent_response, dict):
                        import json
                        agent_response = json.dumps(agent_response, indent=2)
                    elif not isinstance(agent_response, str):
                        # Convert other types to string
                        agent_response = str(agent_response)
                
                # Display payload
                if payload:
                    report.append("**Attack Payload:**\n")
                    report.append("```\n")
                    # Truncate very long payloads but show more than before
                    if len(str(payload)) > 1000:
                        report.append(f"{str(payload)[:1000]}\n... [truncated, full length: {len(str(payload))} chars]\n")
                    else:
                        report.append(f"{payload}\n")
                    report.append("```\n\n")
                
                # Display agent response
                if agent_response:
                    report.append("**Purple Agent Response:**\n")
                    report.append("```\n")
                    if len(str(agent_response)) > 1000:
                        report.append(f"{str(agent_response)[:1000]}\n... [truncated, full length: {len(str(agent_response))} chars]\n")
                    else:
                        report.append(f"{agent_response}\n")
                    report.append("```\n\n")
                else:
                    # Fallback: show full proof_of_concept if we couldn't parse it
                    report.append("```\n")
                    report.append(f"{vuln.proof_of_concept}\n")
                    report.append("```\n\n")
                
                # Detection details
                detected = vuln.metadata.get('detected', False)
                confidence = vuln.metadata.get('confidence', 0.0)
                report.append("**Detection Status:**\n")
                report.append(f"- Detected: {detected}\n")
                report.append(f"- Confidence: {confidence:.2f}\n")
                report.append(f"- Outcome: Attack succeeded (vulnerability exploited)\n\n")
                
                report.append(f"**Remediation:**\n{vuln.remediation}\n\n")
                report.append("---\n\n")
        
        # Remediation Roadmap
        report.append("## 🛠️ Remediation Roadmap\n\n")
        report.append(f"**Estimated Total Fix Time:** {assessment.estimated_fix_time_hours:.1f} hours\n\n")
        
        if assessment.critical_count > 0:
            report.append("### Phase 1: Critical Fixes (Week 1) - IMMEDIATE\n\n")
            report.append(f"- **Vulnerabilities:** {assessment.critical_count} critical issues\n")
            report.append(f"- **Estimated Time:** {assessment.critical_count * 2:.1f} hours\n")
            report.append("- **Priority:** 🔴 IMMEDIATE - Take system offline if necessary\n")
            report.append("- **Impact:** Prevents complete system compromise\n\n")
        
        if assessment.high_count > 0:
            report.append("### Phase 2: High-Severity Fixes (Week 2-3) - URGENT\n\n")
            report.append(f"- **Vulnerabilities:** {assessment.high_count} high-severity issues\n")
            report.append(f"- **Estimated Time:** {assessment.high_count * 1:.1f} hours\n")
            report.append("- **Priority:** 🟠 URGENT - Deploy within 48 hours\n")
            report.append("- **Impact:** Significant risk reduction\n\n")
        
        if assessment.medium_count > 0:
            report.append("### Phase 3: Medium-Severity Fixes (Week 4-5) - IMPORTANT\n\n")
            report.append(f"- **Vulnerabilities:** {assessment.medium_count} medium-severity issues\n")
            report.append(f"- **Estimated Time:** {assessment.medium_count * 0.5:.1f} hours\n")
            report.append("- **Priority:** 🟡 IMPORTANT - Address within 1-2 weeks\n")
            report.append("- **Impact:** Moderate risk reduction\n\n")
        
        report.append("### Phase 4: Security Hardening (Week 6-8) - RECOMMENDED\n\n")
        report.append("- **Focus:** Defense-in-depth, monitoring, ongoing security\n")
        report.append("- **Estimated Time:** 20 hours\n")
        report.append("- **Priority:** 🔵 RECOMMENDED - Long-term security improvement\n\n")
        
        report.append("---\n\n")
        
        # Recommendations
        report.append("## 📋 Immediate Actions Required\n\n")
        report.append(self._generate_recommendations(assessment))
        
        report.append("\n---\n\n")
        report.append(f"*Report generated by Purple Agent Security Reporter on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")
        
        return "".join(report)

    def _get_security_status(self, assessment: PurpleAgentAssessment) -> str:
        """Generate security status message."""
        if assessment.risk_level == "CRITICAL":
            return (
                "🔴 **STATUS: CRITICAL RISK**\n\n"
                "**Recommendation:** System should be taken offline until critical vulnerabilities are fixed."
            )
        elif assessment.risk_level == "HIGH":
            return (
                "🟠 **STATUS: HIGH RISK**\n\n"
                "**Recommendation:** Deploy security fixes within 24-48 hours."
            )
        elif assessment.risk_level == "MEDIUM":
            return (
                "🟡 **STATUS: MEDIUM RISK**\n\n"
                "**Recommendation:** Address vulnerabilities within 1-2 weeks."
            )
        elif assessment.risk_level == "LOW":
            return (
                "🟢 **STATUS: LOW RISK**\n\n"
                "**Recommendation:** Address during next maintenance window."
            )
        else:
            return (
                "✅ **STATUS: MINIMAL RISK**\n\n"
                "**Recommendation:** Continue regular security monitoring and testing."
            )

    def _get_status_icon(self, rate: float, inverse: bool = False) -> str:
        """Get status icon based on rate."""
        # If inverse=True, lower is better (e.g., attack success rate)
        threshold = 20 if inverse else 80
        
        if inverse:
            if rate < 10: return "✅"
            if rate < 30: return "⚠️"
            return "🔴"
        else:
            if rate > 90: return "✅"
            if rate > 70: return "⚠️"
            return "🔴"

    def _generate_recommendations(self, assessment: PurpleAgentAssessment) -> str:
        """Generate immediate action recommendations."""
        report = []
        
        if assessment.critical_count > 0:
            report.append(f"1. 🚨 **CRITICAL:** Address {assessment.critical_count} critical vulnerabilities immediately\n")
            if assessment.priority_fixes:
                report.append(f"   - Priority: {', '.join(assessment.priority_fixes[:3])}\n")
        
        if assessment.high_count > 0:
            report.append(f"2. ⚠️ **URGENT:** Fix {assessment.high_count} high-severity vulnerabilities within 48 hours\n")
        
        if assessment.attack_success_rate > 50:
            report.append(f"3. 🛡️ **SECURITY:** Attack success rate is {assessment.attack_success_rate:.1f}% - implement defense-in-depth\n")
        
        report.append("4. 📊 **MONITORING:** Implement security monitoring and alerting\n")
        report.append("5. 📝 **DOCUMENTATION:** Create incident response plan\n")
        report.append("6. 🔄 **CONTINUOUS:** Schedule quarterly security assessments\n")
        
        return "".join(report)

    def generate_json_report(self, dual_result: DualEvaluationResult) -> Dict[str, Any]:
        """
        Generate JSON format security assessment report.

        Args:
            dual_result: Dual evaluation result

        Returns:
            Dictionary suitable for JSON serialization
        """
        assessment = dual_result.purple_agent_assessment
        
        return {
            "report_type": "purple_agent_security_assessment",
            "evaluation_id": dual_result.evaluation_id,
            "purple_agent": assessment.purple_agent_name,
            "scenario": dual_result.scenario,
            "timestamp": assessment.assessment_date.isoformat(),
            "duration_seconds": dual_result.total_time_seconds,
            
            "security_summary": {
                "security_score": assessment.security_score,
                "security_grade": assessment.security_grade,
                "risk_level": assessment.risk_level,
                "total_vulnerabilities": assessment.total_vulnerabilities
            },
            
            "vulnerability_breakdown": {
                "critical": assessment.critical_count,
                "high": assessment.high_count,
                "medium": assessment.medium_count,
                "low": assessment.low_count,
                "average_cvss": assessment.average_cvss_score,
                "max_cvss": assessment.max_cvss_score
            },
            
            "defense_metrics": {
                "attack_success_rate": assessment.attack_success_rate,
                "defense_success_rate": assessment.defense_success_rate,
                "total_tests": assessment.total_tests
            },
            
            "remediation": {
                "estimated_hours": assessment.estimated_fix_time_hours,
                "priority_fixes": assessment.priority_fixes
            },
            
            "vulnerabilities": [
                {
                    "id": vuln.vulnerability_id,
                    "cvss_score": vuln.cvss_score,
                    "severity": vuln.severity,
                    "cwe_id": vuln.cwe_id,
                    "cwe_name": vuln.cwe_name,
                    "description": vuln.description,
                    "remediation": vuln.remediation
                }
                for vuln in sorted(assessment.vulnerabilities, 
                                  key=lambda v: v.cvss_score, reverse=True)
            ]
        }

    def generate_executive_summary(self, dual_result: DualEvaluationResult) -> str:
        """
        Generate brief executive summary for management.

        Args:
            dual_result: Dual evaluation result

        Returns:
            Brief executive summary
        """
        assessment = dual_result.purple_agent_assessment
        
        return (
            f"{assessment.purple_agent_name} Security Assessment:\n"
            f"Score: {assessment.security_score:.1f}/100 ({assessment.security_grade}) | "
            f"Risk: {assessment.risk_level} | "
            f"Vulnerabilities: {assessment.total_vulnerabilities} "
            f"(C:{assessment.critical_count} H:{assessment.high_count} M:{assessment.medium_count}) | "
            f"Fix Time: {assessment.estimated_fix_time_hours:.0f}h"
        )
