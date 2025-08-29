"""
DSPy signature classes for evaluating DynamoDB guidance quality.
Contains structured evaluation modules for comprehensive assessment.
"""

import dspy
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path

from evaluation_config import EvaluationDimension, SessionDimension, EvaluationConfig


class ScoreDescriptions:
    """Detailed scoring descriptions for DSPy evaluators."""
    
    COMPLETENESS = (
        "Score 1-10: Evaluate if guidance addresses ALL scenario elements: "
        "(1) All entities identified and defined, "
        "(2) All entity relationships mapped, "
        "(3) All access patterns identified (not optimized), "
        "(4) Performance requirements and constraints covered, "
        "(5) Scale requirements and constraints covered. "
        "Score 9-10: Comprehensive coverage of all elements. "
        "Score 7-8: Most elements covered with minor gaps. "
        "Score 5-6: Core elements but missing important details. "
        "Score 3-4: Significant gaps in key elements. "
        "Score 1-2: Major elements missing. "
        "Return single number 1-10, not 8/10"
    )
    
    TECHNICAL_ACCURACY = (
        "Score 1-10: Evaluate technical correctness of DynamoDB recommendations: "
        "(1) Primary key design follows best practices, "
        "(2) GSI design is appropriate and efficient including the use of projections where relevant, "
        "(3) Data types and attribute choices are optimal (TTL as number, etc.), "
        "(4) Sort key design enables required access patterns, "
        "(5) Recommendations follow DynamoDB best practices. "
        "Score 9-10: All recommendations technically sound with deep expertise. "
        "Score 7-8: Mostly accurate with only minor technical issues. "
        "Score 5-6: Generally accurate but some questionable recommendations. "
        "Score 3-4: Several technical errors or best practice violations. "
        "Score 1-2: Major technical errors, fundamental DynamoDB misunderstandings. "
        "Return single number 1-10."
    )
    
    ACCESS_PATTERN_COVERAGE = (
        "Score 1-10: Evaluate how well access patterns are optimized: "
        "(1) Query patterns mapped to optimal table/GSI design, "
        "(2) Solutions optimize for most frequent/critical patterns, "
        "(3) Edge cases and less frequent patterns considered, "
        "(4) Performance implications of each pattern addressed, "
        "(5) Efficient query strategies recommended. "
        "Score 9-10: Identifies and addresses all critical patterns with optimized solutions. "
        "Score 7-8: Covers most important patterns with effective solutions. "
        "Score 5-6: Addresses core patterns but misses some important ones. "
        "Score 3-4: Limited coverage, solutions may be inefficient. "
        "Score 1-2: Poor understanding of patterns, inadequate solutions. "
        "Return single number 1-10."
    )
    
    SCALABILITY_CONSIDERATIONS = (
        "Score 1-10: Evaluate scalability and performance planning: "
        "(1) Hot partition prevention strategies, "
        "(2) Capacity planning for expected growth, "
        "(3) Performance bottleneck identification, "
        "(4) Auto-scaling considerations, "
        "(5) Future growth accommodation in design. "
        "Score 9-10: Comprehensive scalability analysis with proactive solutions for bottlenecks. "
        "Score 7-8: Good scalability awareness with most key considerations addressed. "
        "Score 5-6: Basic scalability considerations with some important aspects covered. "
        "Score 3-4: Limited scalability planning, may have scaling issues. "
        "Score 1-2: No meaningful scalability considerations, designs likely to fail at scale. "
        "Return single number 1-10."
    )
    
    COST_OPTIMIZATION = (
        "Score 1-10: Evaluate cost optimization strategies: "
        "(1) On-demand vs provisioned billing analysis, "
        "(2) GSI cost implications considered, "
        "(3) Storage cost optimization strategies, "
        "(4) Read/write cost efficiency recommendations, "
        "(5) Multiple cost-saving techniques suggested. "
        "Score 9-10: Sophisticated cost optimization with multiple strategies. "
        "Score 7-8: Good cost awareness with several optimization techniques. "
        "Score 5-6: Basic cost considerations with some optimization suggestions. "
        "Score 3-4: Limited cost analysis, may lead to unnecessary expenses. "
        "Score 1-2: No cost optimization, designs likely to be expensive. "
        "Return single number 1-10."
    )



class DynamoDBGuidanceEvaluator(dspy.Signature):
    """
    Primary evaluator for overall DynamoDB guidance quality.
    Assesses completeness, technical accuracy, and adherence to best practices.
    """
    
    # Input context
    scenario_requirements = dspy.InputField(
        desc="Complete scenario requirements including entities, access patterns, scale, and performance needs"
    )
    guidance_response = dspy.InputField(
        desc="The AI-generated DynamoDB guidance response to evaluate"
    )
    dynamodb_expert_knowledge = dspy.InputField(
        desc="Comprehensive DynamoDB expert guidance including best practices, design patterns, technical constraints, and cost optimization strategies to inform evaluation scoring"
    )
    
    # Core evaluation scores (1-10 scale)
    completeness_score = dspy.OutputField(desc=ScoreDescriptions.COMPLETENESS)
    
    technical_accuracy_score = dspy.OutputField(desc=ScoreDescriptions.TECHNICAL_ACCURACY)
    
    access_pattern_coverage_score = dspy.OutputField(desc=ScoreDescriptions.ACCESS_PATTERN_COVERAGE)
    
    scalability_considerations_score = dspy.OutputField(desc=ScoreDescriptions.SCALABILITY_CONSIDERATIONS)
    
    cost_optimization_score = dspy.OutputField(desc=ScoreDescriptions.COST_OPTIMIZATION)
    
    # Detailed justifications
    completeness_justification = dspy.OutputField(
        desc="Detailed explanation of completeness score, highlighting what was covered well and what was missed"
    )
    
    technical_justification = dspy.OutputField(
        desc="Detailed explanation of technical accuracy, noting correct and incorrect recommendations"
    )
    
    overall_assessment = dspy.OutputField(
        desc="Overall quality assessment with strengths, weaknesses, and improvement suggestions"
    )


class DynamoDBSessionEvaluator(dspy.Signature):
    """
    Evaluator for DynamoDB modeling session methodology and process quality.
    Assesses requirements gathering, methodology, and documentation quality.
    """
    
    # Input context
    scenario_requirements = dspy.InputField(
        desc="Original business requirements and constraints provided by user"
    )
    modeling_session_content = dspy.InputField(
        desc="Complete modeling session output including analysis, methodology, and validation"
    )
    architect_methodology = dspy.InputField(
        desc="DynamoDB architect prompt methodology and best practices for reference"
    )
    
    # Session-specific evaluation scores (1-10 scale)
    requirements_engineering_score = dspy.OutputField(
        desc="Score 1-10: Quality of requirements capture, entity modeling, and scope definition. Are business context, scale, and constraints properly documented? Should be just a number between 1-10"
    )
    
    access_pattern_analysis_score = dspy.OutputField(
        desc="Score 1-10: Rigor of access pattern analysis including completeness, RPS estimates, performance requirements, and prioritization. Should be just a number between 1-10"
    )
    
    methodology_adherence_score = dspy.OutputField(
        desc="Score 1-10: How well does the session follow the systematic methodology from the architect prompt? Are decision frameworks properly applied? Should be just a number between 1-10"
    )
    
    technical_reasoning_score = dspy.OutputField(
        desc="Score 1-10: Quality of design justifications, trade-off analysis, risk assessment, and optimization considerations. Should be just a number between 1-10"
    )
    
    process_documentation_score = dspy.OutputField(
        desc="Score 1-10: Organization, transparency, traceability, and professional quality of process documentation. Should be just a number between 1-10"
    )
    
    # Detailed analysis
    requirements_analysis = dspy.OutputField(
        desc="Detailed assessment of requirements engineering quality, highlighting strengths and gaps"
    )
    
    methodology_assessment = dspy.OutputField(
        desc="Evaluation of how well the structured methodology was followed, including decision framework usage"
    )
    
    technical_depth_evaluation = dspy.OutputField(
        desc="Analysis of technical reasoning quality, design justifications, and proactive risk identification"
    )
    
    overall_session_assessment = dspy.OutputField(
        desc="Overall evaluation of the modeling session quality with specific recommendations for improvement"
    )


@dataclass
class EvaluationResult:
    """Structured result from DSPy evaluations."""
    
    # Core scores
    completeness: float
    technical_accuracy: float  
    access_pattern_coverage: float
    scalability_considerations: float
    cost_optimization: float
    
    # Detailed analysis
    justifications: Dict[str, str]
    
    # Overall assessment
    overall_score: float
    quality_level: str


@dataclass
class SessionEvaluationResult:
    """Structured result from DSPy session evaluations."""
    
    # Core session scores
    requirements_engineering: float
    access_pattern_analysis: float
    methodology_adherence: float
    technical_reasoning: float
    process_documentation: float
    
    # Detailed analysis
    justifications: Dict[str, str]
    
    # Overall session assessment
    overall_score: float
    quality_level: str


class DSPyEvaluationEngine:
    """
    Orchestrates DSPy evaluation modules for comprehensive assessment.
    Coordinates multiple evaluators and aggregates results.
    """
    
    def __init__(self, architect_prompt_path: Optional[str] = None):
        """
        Initialize DSPy evaluation modules.
        
        Args:
            architect_prompt_path: Path to DynamoDB architect prompt file. 
                                 Defaults to the standard location if not provided.
        """
        self.guidance_evaluator = dspy.ChainOfThought(DynamoDBGuidanceEvaluator)
        self.session_evaluator = dspy.ChainOfThought(DynamoDBSessionEvaluator)
        
        # Set default path relative to current working directory
        if architect_prompt_path is None:
            architect_prompt_path = "src/dynamodb-mcp-server/awslabs/dynamodb_mcp_server/prompts/dynamodb_architect.md"
        
        self.architect_prompt_path = architect_prompt_path
        self._expert_knowledge_cache = None
    
    def _load_expert_knowledge(self) -> str:
        """
        Load DynamoDB expert guidance from markdown file.
        Uses caching to avoid repeated file reads.
        
        Returns:
            String content of the expert guidance document
            
        Raises:
            FileNotFoundError: If the architect prompt file cannot be found
            IOError: If there are issues reading the file
        """
        if self._expert_knowledge_cache is None:
            try:
                prompt_path = Path(self.architect_prompt_path)
                
                # Try relative to current working directory first
                if not prompt_path.exists():
                    # Try relative to this file's directory as fallback
                    current_dir = Path(__file__).parent
                    fallback_path = current_dir / ".." / ".." / "awslabs" / "dynamodb_mcp_server" / "prompts" / "dynamodb_architect.md"
                    if fallback_path.exists():
                        prompt_path = fallback_path
                    else:
                        raise FileNotFoundError(f"DynamoDB architect prompt not found at {self.architect_prompt_path} or fallback location")
                
                with open(prompt_path, 'r', encoding='utf-8') as file:
                    self._expert_knowledge_cache = file.read()
                    
            except Exception as e:
                # Provide fallback empty knowledge with error info
                fallback_msg = f"Error loading DynamoDB expert knowledge: {str(e)}. Using minimal context for evaluation."
                print(f"Warning: {fallback_msg}")
                self._expert_knowledge_cache = fallback_msg
        
        return self._expert_knowledge_cache
    
    def evaluate_guidance(self, scenario: Dict[str, Any], response: str) -> EvaluationResult:
        """
        Run comprehensive evaluation using all DSPy modules.
        
        Args:
            scenario: Complete scenario specification
            response: AI-generated guidance response
            
        Returns:
            EvaluationResult with comprehensive scoring and analysis
        """     
        # Load expert knowledge for evaluation context
        expert_knowledge = self._load_expert_knowledge()
        
        # Run overall guidance evaluation with expert context
        guidance_result = self.guidance_evaluator(
            scenario_requirements=self._build_scenario_summary(scenario),
            guidance_response=response,
            dynamodb_expert_knowledge=expert_knowledge
        )

        print("guidance_result")
        print(guidance_result)
      
        # Aggregate results
        return self._aggregate_evaluation_results(
            guidance_result
        )
    
    def evaluate_session(self, scenario: Dict[str, Any], session_content: str) -> SessionEvaluationResult:
        """
        Run comprehensive session evaluation using DSPy modules.
        
        Args:
            scenario: Complete scenario specification
            session_content: AI-generated modeling session content
            
        Returns:
            SessionEvaluationResult with comprehensive scoring and analysis
        """
        # Load expert knowledge for evaluation context
        expert_knowledge = self._load_expert_knowledge()
        
        # Run session evaluation with expert context
        session_result = self.session_evaluator(
            scenario_requirements=self._build_scenario_summary(scenario),
            modeling_session_content=session_content,
            architect_methodology=expert_knowledge
        )

        print("session_result")
        print(session_result)
        
        # Aggregate session results
        return self._aggregate_session_evaluation_results(
            session_result
        )
    
    def _build_scenario_summary(self, scenario: Dict[str, Any]) -> str:
        """Build comprehensive scenario summary for evaluation."""
        parts = [
            f"Scenario: {scenario.get('name', 'Unknown')}",
            f"Complexity: {scenario.get('complexity', 'beginner')}",
            f"Description: {scenario.get('description', '')}"
        ]
        
        if 'entities_and_relationships' in scenario:
            parts.append(f"Entities: {scenario['entities_and_relationships']}")
            
        if 'access_patterns' in scenario:
            parts.append(f"Access Patterns: {scenario['access_patterns']}")
            
        if 'performance_and_scale' in scenario:
            parts.append(f"Scale Requirements: {scenario['performance_and_scale']}")
            
        return "\n".join(parts)
    
    def _aggregate_evaluation_results(self, 
                                        guidance_result) -> EvaluationResult:
        """Aggregate results from all evaluation modules."""
        
        # Extract scores (convert to float, handle potential string responses)
        def safe_float(value, default=0.0):
            try:
                return float(str(value).split()[0]) if value else default
            except (ValueError, IndexError):
                return default
  
        
        scores = {
            EvaluationDimension.COMPLETENESS: safe_float(guidance_result.completeness_score),
            EvaluationDimension.TECHNICAL_ACCURACY: safe_float(guidance_result.technical_accuracy_score),
            EvaluationDimension.ACCESS_PATTERN_COVERAGE: safe_float(guidance_result.access_pattern_coverage_score),
            EvaluationDimension.SCALABILITY_CONSIDERATIONS: safe_float(guidance_result.scalability_considerations_score),
            EvaluationDimension.COST_OPTIMIZATION: safe_float(guidance_result.cost_optimization_score),
        }
        
        # Calculate overall weighted score
        overall_score = EvaluationConfig.calculate_weighted_score(scores)
        quality_level = EvaluationConfig.get_quality_level(overall_score)
        
        return EvaluationResult(
            completeness=scores[EvaluationDimension.COMPLETENESS],
            technical_accuracy=scores[EvaluationDimension.TECHNICAL_ACCURACY],
            access_pattern_coverage=scores[EvaluationDimension.ACCESS_PATTERN_COVERAGE],
            scalability_considerations=scores[EvaluationDimension.SCALABILITY_CONSIDERATIONS],
            cost_optimization=scores[EvaluationDimension.COST_OPTIMIZATION],
            
            justifications={
                'completeness': str(guidance_result.completeness_justification),
                'technical': str(guidance_result.technical_justification),
                'overall': str(guidance_result.overall_assessment)
            },
            
            overall_score=overall_score,
            quality_level=quality_level
        )
    
    def _aggregate_session_evaluation_results(self, session_result) -> SessionEvaluationResult:
        """Aggregate results from session evaluation modules."""
        
        # Extract scores (convert to float, handle potential string responses)
        def safe_float(value, default=0.0):
            try:
                return float(str(value).split()[0]) if value else default
            except (ValueError, IndexError):
                return default
        
        scores = {
            SessionDimension.REQUIREMENTS_ENGINEERING: safe_float(session_result.requirements_engineering_score),
            SessionDimension.ACCESS_PATTERN_ANALYSIS: safe_float(session_result.access_pattern_analysis_score),
            SessionDimension.METHODOLOGY_ADHERENCE: safe_float(session_result.methodology_adherence_score),
            SessionDimension.TECHNICAL_REASONING: safe_float(session_result.technical_reasoning_score),
            SessionDimension.PROCESS_DOCUMENTATION: safe_float(session_result.process_documentation_score),
        }
        
        # Calculate overall weighted score for session
        overall_score = EvaluationConfig.calculate_session_weighted_score(scores)
        quality_level = EvaluationConfig.get_quality_level(overall_score)
        
        return SessionEvaluationResult(
            requirements_engineering=scores[SessionDimension.REQUIREMENTS_ENGINEERING],
            access_pattern_analysis=scores[SessionDimension.ACCESS_PATTERN_ANALYSIS],
            methodology_adherence=scores[SessionDimension.METHODOLOGY_ADHERENCE],
            technical_reasoning=scores[SessionDimension.TECHNICAL_REASONING],
            process_documentation=scores[SessionDimension.PROCESS_DOCUMENTATION],
            
            justifications={
                'requirements': str(session_result.requirements_analysis),
                'methodology': str(session_result.methodology_assessment),
                'technical_depth': str(session_result.technical_depth_evaluation),
                'overall': str(session_result.overall_session_assessment)
            },
            
            overall_score=overall_score,
            quality_level=quality_level
        )


# Export key classes for easy importing
__all__ = [
    'DynamoDBGuidanceEvaluator',
    'DynamoDBSessionEvaluator',
    'DSPyEvaluationEngine',
    'EvaluationResult',
    'SessionEvaluationResult'
]
