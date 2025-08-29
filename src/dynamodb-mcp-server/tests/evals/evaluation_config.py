"""
Configuration for DynamoDB guidance evaluation system.
Defines scoring rubrics, criteria, and evaluation parameters.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

class EvaluationDimension(Enum):
    """Core dimensions for evaluating DynamoDB guidance quality."""
    COMPLETENESS = "completeness"
    TECHNICAL_ACCURACY = "technical_accuracy"
    ACCESS_PATTERN_COVERAGE = "access_pattern_coverage"
    SCALABILITY_CONSIDERATIONS = "scalability_considerations"
    COST_OPTIMIZATION = "cost_optimization"


class SessionDimension(Enum):
    """Core dimensions for evaluating DynamoDB modeling session quality."""
    REQUIREMENTS_ENGINEERING = "requirements_engineering"
    ACCESS_PATTERN_ANALYSIS = "access_pattern_analysis"
    METHODOLOGY_ADHERENCE = "methodology_adherence"
    TECHNICAL_REASONING = "technical_reasoning"
    PROCESS_DOCUMENTATION = "process_documentation"


@dataclass
class ScoringCriteria:
    """Defines scoring criteria for a specific evaluation dimension."""
    
    excellent: str  # 9-10 score criteria
    good: str       # 7-8 score criteria  
    fair: str       # 5-6 score criteria
    poor: str       # 3-4 score criteria
    failing: str    # 1-2 score criteria
    
    def get_score_description(self, score: int) -> str:
        """Get description for a given numeric score."""
        if score >= 9:
            return self.excellent
        elif score >= 7:
            return self.good
        elif score >= 5:
            return self.fair
        elif score >= 3:
            return self.poor
        else:
            return self.failing


class EvaluationConfig:
    """Central configuration for DynamoDB guidance evaluation."""
    
    # Core scoring criteria for each dimension
    # SCORING_CRITERIA = {
    #     EvaluationDimension.COMPLETENESS: ScoringCriteria(
    #         excellent="Addresses all entities, relationships, access patterns, and performance requirements with comprehensive detail",
    #         good="Addresses most requirements with only minor gaps in coverage",
    #         fair="Addresses core requirements but misses some important details or considerations", 
    #         poor="Partial coverage with significant gaps in key requirements",
    #         failing="Minimal coverage, major requirements completely unaddressed"
    #     ),
        
    #     EvaluationDimension.TECHNICAL_ACCURACY: ScoringCriteria(
    #         excellent="All DynamoDB recommendations are technically sound, follow best practices, and demonstrate deep expertise",
    #         good="Mostly accurate recommendations with only minor technical issues",
    #         fair="Generally accurate but contains some questionable or suboptimal recommendations",
    #         poor="Several technical errors or recommendations that violate best practices",
    #         failing="Major technical errors, fundamental misunderstandings of DynamoDB concepts"
    #     ),
        
    #     EvaluationDimension.ACCESS_PATTERN_COVERAGE: ScoringCriteria(
    #         excellent="Identifies and addresses all critical access patterns with optimized solutions",
    #         good="Covers most important access patterns with effective solutions", 
    #         fair="Addresses core access patterns but misses some important ones",
    #         poor="Limited coverage of access patterns, solutions may be inefficient",
    #         failing="Poor understanding of access patterns, inadequate solutions"
    #     ),
        
    #     EvaluationDimension.SCALABILITY_CONSIDERATIONS: ScoringCriteria(
    #         excellent="Comprehensive scalability analysis with proactive solutions for potential bottlenecks",
    #         good="Good scalability awareness with most key considerations addressed",
    #         fair="Basic scalability considerations with some important aspects covered",
    #         poor="Limited scalability planning, may have scaling issues",
    #         failing="No meaningful scalability considerations, designs likely to fail at scale"
    #     ),
        
    #     EvaluationDimension.COST_OPTIMIZATION: ScoringCriteria(
    #         excellent="Sophisticated cost optimization with RPS-based calculations and multiple cost-saving strategies",
    #         good="Good cost awareness with proper calculations and several optimization techniques",
    #         fair="Basic cost considerations with some optimization suggestions",
    #         poor="Limited cost analysis, may lead to unnecessary expenses", 
    #         failing="No cost optimization, designs likely to be expensive"
    #     )
    # }
    
    # Session scoring criteria for modeling process evaluation
    # SESSION_SCORING_CRITERIA = {
    #     SessionDimension.REQUIREMENTS_ENGINEERING: ScoringCriteria(
    #         excellent="Complete application context with business model, scale, entities, relationships, and constraints properly documented with realistic estimates",
    #         good="Most requirements captured with clear business context and entity modeling, minor gaps in constraints or scale estimates",
    #         fair="Basic requirements documented but missing some business context, entity relationships, or scale considerations",
    #         poor="Limited requirements capture with significant gaps in business understanding or entity modeling",
    #         failing="Minimal or missing requirements documentation, poor understanding of business context and entities"
    #     ),
        
    #     SessionDimension.ACCESS_PATTERN_ANALYSIS: ScoringCriteria(
    #         excellent="All CRUD operations identified with realistic RPS estimates (peak/average), performance requirements, and proper prioritization",
    #         good="Most access patterns identified with good RPS estimates and performance requirements, minor gaps in completeness",
    #         fair="Core access patterns documented with some RPS estimates, but missing some patterns or performance requirements",
    #         poor="Limited access pattern analysis with few RPS estimates and unclear performance requirements",
    #         failing="Poor or missing access pattern analysis, no RPS estimates, unclear requirements"
    #     ),
        
    #     SessionDimension.METHODOLOGY_ADHERENCE: ScoringCriteria(
    #         excellent="Perfect adherence to architect prompt structure with systematic consolidation analysis, decision frameworks, and complete validation",
    #         good="Good methodology following with structured analysis and most validation items completed",
    #         fair="Basic methodology following but missing some systematic analysis or validation steps",
    #         poor="Limited methodology adherence with ad-hoc analysis and incomplete validation",
    #         failing="No systematic methodology followed, missing structure and validation"
    #     ),
        
    #     SessionDimension.TECHNICAL_REASONING: ScoringCriteria(
    #         excellent="Clear quantitative justifications for all design decisions with explicit trade-off analysis and proactive risk identification",
    #         good="Good design reasoning with most decisions justified and trade-offs considered",
    #         fair="Basic design justifications provided but missing some trade-off analysis or risk assessment",
    #         poor="Limited design reasoning with weak justifications and minimal trade-off consideration",
    #         failing="Poor or missing design justifications, no trade-off analysis, no risk assessment"
    #     ),
        
    #     SessionDimension.PROCESS_DOCUMENTATION: ScoringCriteria(
    #         excellent="Professional-quality documentation with clear traceability from requirements to decisions, well-organized, enables effective handoff",
    #         good="Good documentation organization with clear traceability and professional presentation",
    #         fair="Adequate documentation with some organization and traceability",
    #         poor="Limited documentation quality with poor organization and unclear traceability",
    #         failing="Poor documentation quality, disorganized, unclear traceability"
    #     )
    # }
 
    QUALITY_THRESHOLDS = {
        "excellent": 8.5,
        "good": 7.0,
        "acceptable": 5.5,
        "needs_improvement": 4.0,
        "poor": 2.0
    }
        
    # @classmethod
    # def get_scoring_criteria(cls, dimension: EvaluationDimension) -> ScoringCriteria:
    #     """Get scoring criteria for a specific evaluation dimension."""
    #     return cls.SCORING_CRITERIA[dimension]
    
    # @classmethod
    # def get_session_scoring_criteria(cls, dimension: SessionDimension) -> ScoringCriteria:
    #     """Get scoring criteria for a specific session evaluation dimension."""
    #     return cls.SESSION_SCORING_CRITERIA[dimension]
    
    @classmethod
    def calculate_weighted_score(cls, scores: Dict[EvaluationDimension, float]) -> float:
        """Calculate overall weighted score based on complexity."""
        
        weighted_sum = (
            scores[EvaluationDimension.COMPLETENESS] +
            scores[EvaluationDimension.TECHNICAL_ACCURACY]  +
            scores[EvaluationDimension.ACCESS_PATTERN_COVERAGE] +
            scores[EvaluationDimension.SCALABILITY_CONSIDERATIONS] +
            scores[EvaluationDimension.COST_OPTIMIZATION]  
        ) / len(EvaluationDimension)
        
        return round(weighted_sum, 2)
    
    @classmethod
    def calculate_session_weighted_score(cls, scores: Dict[SessionDimension, float]) -> float:
        """Calculate overall weighted score for session evaluation."""
        
        weighted_sum = (
            scores[SessionDimension.REQUIREMENTS_ENGINEERING] +
            scores[SessionDimension.ACCESS_PATTERN_ANALYSIS] +
            scores[SessionDimension.METHODOLOGY_ADHERENCE] +
            scores[SessionDimension.TECHNICAL_REASONING] +
            scores[SessionDimension.PROCESS_DOCUMENTATION]
        ) / len(SessionDimension)
        
        return round(weighted_sum, 2)
    
    @classmethod
    def get_quality_level(cls, score: float) -> str:
        """Determine quality level based on numeric score."""
        if score >= cls.QUALITY_THRESHOLDS["excellent"]:
            return "excellent"
        elif score >= cls.QUALITY_THRESHOLDS["good"]:
            return "good"
        elif score >= cls.QUALITY_THRESHOLDS["acceptable"]:
            return "acceptable"
        elif score >= cls.QUALITY_THRESHOLDS["needs_improvement"]:
            return "needs_improvement"
        else:
            return "poor"


# Export key classes and enums for easy importing
__all__ = [
    'EvaluationConfig',
    'EvaluationDimension',
    'SessionDimension',
    'ScoringCriteria',
]
