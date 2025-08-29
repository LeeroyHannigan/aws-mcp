"""
Multi-turn conversation evaluator for DynamoDB MCP tool using Strands agents.
Tests the tool through realistic interactive conversations with native MCP integration.
Enhanced with comprehensive DSPy evaluation capabilities.
"""

import asyncio
import time
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from botocore.config import Config as BotocoreConfig
import os
import re
import dspy

from strands import Agent
from strands.models import BedrockModel
from strands.tools.mcp import MCPClient
from mcp import stdio_client, StdioServerParameters
from evaluation_config import EvaluationConfig
from dspy_evaluators import DSPyEvaluationEngine, EvaluationResult, SessionEvaluationResult


@dataclass
class ConversationTurn:
    """Represents a single turn in the conversation."""
    role: str  # 'user' or 'assistant' 
    content: str
    turn_number: int
    timestamp: float


@dataclass
class ConversationResult:
    """Result of a complete conversation evaluation."""
    turns: List[ConversationTurn]

def _to_text(x) -> str:
    """Best-effort conversion of varied agent outputs to plain text."""
    if isinstance(x, str):
        return x
    for attr in ("message", "text", "content"):
        v = getattr(x, attr, None)
        if isinstance(v, str):
            return v
    try:
        return str(x)
    except Exception:
        return ""
    
import ast
import re

def extract_guidance_sections(final_guidance):
    """
    Extract two markdown sections from final_guidance string.
    
    Args:
        final_guidance: String containing the JSON response from the agent
        
    Returns:
        tuple: (dynamodb_modeling_session, dynamodb_data_model)
    """
    
    # Step 1: Parse the string as a Python dictionary
    try:
        response_data = ast.literal_eval(final_guidance)
    except (ValueError, SyntaxError) as e:
        print(f"Error parsing final_guidance: {e}")
        return None, None
    
    # Step 2: Extract the markdown content from the nested structure
    try:
        markdown_content = response_data['content'][0]['text']
    except (KeyError, IndexError) as e:
        print(f"Error accessing content: {e}")
        return None, None
    
    # Step 3: Clean up escaped newlines
    markdown_content = markdown_content.replace('\\n', '\n')
    
    # Step 4: Split into markdown sections
    # The content contains two separate ```markdown blocks
    markdown_blocks = markdown_content.split('```markdown\n')
    
    if len(markdown_blocks) < 3:
        print("Error: Expected at least 2 markdown sections")
        return None, None
    
    # Extract each section (remove closing ``` and strip whitespace)
    dynamodb_modeling_session = markdown_blocks[1].split('```')[0].strip()
    dynamodb_data_model = markdown_blocks[2].split('```')[0].strip()
    
    return dynamodb_modeling_session, dynamodb_data_model

class StrandsConversationHandler:
    """Handles conversations using Strands agents with native MCP integration."""
    
    def __init__(self, model_id: str = "us.anthropic.claude-sonnet-4-20250514-v1:0"):
        """Initialize the Strands conversation handler."""
        normalized = model_id
        if normalized.startswith("bedrock/"):
            normalized = normalized.split("/", 1)[1]
        self.model_id = normalized
        boto_config = BotocoreConfig(
            retries={"max_attempts": 3, "mode": "standard"},
            connect_timeout=5,
            read_timeout=3600
        )
        self.bedrock_model = BedrockModel(
            model_id=self.model_id,
            temperature=0.3,
            streaming=False, 
            boto_client_config=boto_config,
        )
        
    def _setup_mcp_client(self):
        """Set up the DynamoDB MCP client."""
        return MCPClient(
            lambda: stdio_client(StdioServerParameters(
                command="uvx",
                args=["awslabs.dynamodb-mcp-server@latest"],
            ))
        )
    
    def _build_comprehensive_message(self, scenario: Dict[str, Any]) -> str:
        """Build comprehensive user message with all scenario context."""
        
        parts = [
            scenario['user_input'],
            "\nHere are the complete requirements:",
            "What type of application are you building?",
        ]
        
        # Add application details
        app_details = scenario.get('application_details', {})
        if app_details:
            parts.extend([
                f"• Type: {app_details.get('type', 'Not specified')}",
                f"• Domain: {app_details.get('domain', 'Not specified')}",
                f"• Primary Function: {app_details.get('primary_function', 'Not specified')}",
                f"• Business Model: {app_details.get('business_model', 'Not specified')}",
                ""
            ])
        
        # Add entities and relationships
        entities_rel = scenario.get('entities_and_relationships', {})
        if entities_rel:
            parts.append("What are the main entities in your system?")
            
            # Entities
            entities = entities_rel.get('entities', {})
            if entities:
                parts.append("Entities:")
                for entity, description in entities.items():
                    parts.append(f"• {entity}: {description}")
                parts.append("")
            
            # Relationships
            relationships = entities_rel.get('relationships', [])
            if relationships:
                parts.append("Relationships:")
                for relationship in relationships:
                    parts.append(f"• {relationship}")
                parts.append("")
        
        # Add access patterns
        access_patterns = scenario.get('access_patterns', {})
        if access_patterns:
            parts.append("ACCESS PATTERNS:")
            
            # Read patterns
            read_patterns = access_patterns.get('read_patterns', [])
            if read_patterns:
                parts.append("Read Patterns:")
                for pattern in read_patterns:
                    parts.append(f"• {pattern}")
                parts.append("")
            
            # Write patterns
            write_patterns = access_patterns.get('write_patterns', [])
            if write_patterns:
                parts.append("Write Patterns:")
                for pattern in write_patterns:
                    parts.append(f"• {pattern}")
                parts.append("")
        
        # Add performance and scale requirements
        perf_scale = scenario.get('performance_and_scale', {})
        if perf_scale:
            parts.append("What's the expected scale?")
            parts.append(f"• User Base: {perf_scale.get('user_base', 'Not specified')}")
            parts.append(f"• Transaction Volume: {perf_scale.get('transaction_volume', 'Not specified')}")
            parts.append(f"• Data Growth: {perf_scale.get('data_growth', 'Not specified')}")
            parts.append(f"• Read/Write Ratio: {perf_scale.get('read_write_ratio', 'Not specified')}")
            
            # Performance requirements
            perf_reqs = perf_scale.get('performance_requirements', [])
            if perf_reqs:
                parts.append("Performance Requirements:")
                for req in perf_reqs:
                    parts.append(f"• {req}")
            
            parts.extend([
                f"• Scalability Needs: {perf_scale.get('scalability_needs', 'Not specified')}", 
                f"• Regional Requirements: {perf_scale.get('regional_requirements', 'Not specified')}",
                ""
            ])
        
        # Add directive for complete guidance
        parts.extend([
            "INSTRUCTIONS:",
            "Provide complete guidance now. Output exactly two blocks:",
            "1) ```markdown\n# DynamoDB Modeling Session (dynamodb_requirement.md)\n...content...\n```",
            "2) ```markdown\n# DynamoDB Data Model (dynamodb_data_model.md)\n...content...\n```",
            "Do not ask additional questions - provide complete guidance now."
        ])
        
        return "\n".join(parts)
    
    async def simulate_conversation(self, scenario: Dict[str, Any]) -> tuple[str, List[ConversationTurn]]:
        """
        Simulate a 2-turn conversation using Strands agent with MCP integration.
        
        Returns:
            tuple: (final_guidance, conversation_turns)
        """
        conversation = []
        start_time = time.time()
        
        try:
            # Set up MCP client for DynamoDB expert system
            dynamodb_mcp_client = self._setup_mcp_client()
            
            with dynamodb_mcp_client:
                # Get available tools from MCP server
                tools = dynamodb_mcp_client.list_tools_sync()
                
                # Create Strands agent with DynamoDB MCP tools
                agent = Agent(
                    model=self.bedrock_model,
                    tools=tools
                )
                
                # Turn 1: Initial engagement
                turn1_message = "I need help designing a DynamoDB schema. Can you help me understand your approach?"
                
                conversation.append(ConversationTurn(
                    role="user", 
                    content=turn1_message,
                    turn_number=1,
                    timestamp=time.time()
                ))
                
                turn1_response = agent(turn1_message)
                turn1_text = _to_text(turn1_response)

                conversation.append(ConversationTurn(
                    role="assistant",
                    content=turn1_text,
                    turn_number=2,
                    timestamp=time.time()
                ))
                
                # Turn 2: Comprehensive scenario
                comprehensive_message = self._build_comprehensive_message(scenario)
                
                conversation.append(ConversationTurn(
                    role="user",
                    content=comprehensive_message, 
                    turn_number=3,
                    timestamp=time.time()
                ))
                
                turn2_response = agent(comprehensive_message).message
                
                conversation.append(ConversationTurn(
                    role="assistant",
                    content=_to_text(turn2_response),
                    turn_number=4, 
                    timestamp=time.time()
                ))
                
                return _to_text(turn2_response), conversation
                
        except Exception as e:
            print(f"❌ Error during Strands conversation: {e}")
            import traceback
            traceback.print_exc()
            return f"Error during conversation: {str(e)}", conversation


@dataclass
class ComprehensiveEvaluationResult:
    """Enhanced result structure with complete evaluation data."""    
    # Content sections
    modeling_session: str
    data_model: str
    conversation: List[ConversationTurn]
    
    # Separate evaluation results
    session_evaluation: Optional[SessionEvaluationResult] = None
    model_evaluation: Optional[EvaluationResult] = None
    
    # Performance metadata
    conversation_duration: float = 0.0
    session_evaluation_duration: float = 0.0
    model_evaluation_duration: float = 0.0
    timestamp: str = ""
    
    # Separate quality assessments
    session_quality_level: str = "unknown"
    model_quality_level: str = "unknown"
    


class EnhancedMultiTurnEvaluator:
    """
    Enhanced evaluator with comprehensive DSPy evaluation capabilities.
    Combines conversation collection with detailed quality assessment.
    """
    
    def __init__(self, lm_model: str = ""):
        """Initialize the enhanced multi-turn evaluator."""
        try:            
            # Use Strands for conversation handling
            self.conversation_handler = StrandsConversationHandler(lm_model)
            
            # Initialize evaluation components
           
            self.dspy_engine = DSPyEvaluationEngine()
            # self.evaluation_config = EvaluationConfig()
            if not os.environ.get("AWS_DEFAULT_REGION"):
                os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
            
            # Ensure DSPy uses the same model as Strands
            dspy_model = lm_model
            if not dspy_model.startswith("bedrock/"):
                dspy_model = f"bedrock/{dspy_model}"
            
            dspy.configure(lm=dspy.LM(dspy_model, max_tokens=8192))
            print(f"✅ DSPy configured with {dspy_model}")
            
            
        except Exception as e:
            print(f"Warning: Could not configure EnhancedMultiTurnEvaluator: {e}")
    
    async def evaluate_with_conversation(self, scenario: Dict[str, Any]) -> Optional[ComprehensiveEvaluationResult]:
        """
        Enhanced evaluation with comprehensive DSPy scoring and analysis.
        
        Args:
            scenario: Complete scenario specification
            
        Returns:
            ComprehensiveEvaluationResult with conversation and evaluation data
        """
        # if not self.configured:
        #     print("❌ Evaluator not properly configured")
        #     return None
        
        start_time = time.time()
        
        try:
            # Step 1: Run conversation collection
            print(f"🔄 Running conversation for scenario: {scenario.get('name', 'Unknown')}")
            conversation_start = time.time()
            
            final_guidance, conversation = await self.conversation_handler.simulate_conversation(scenario)
            conversation_duration = time.time() - conversation_start

            print("final_guidance")
            print("---------------")
            print("---------------")
            print(final_guidance)

            dynamodb_modeling_session, dynamodb_data_model = extract_guidance_sections(final_guidance)
            print("dynamodb_modeling_session")
            print("---------------")
            print(dynamodb_modeling_session)

            print("dynamodb_data_model")
            print("---------------")
            print(dynamodb_data_model)

            print(f"✅ Conversation completed in {conversation_duration:.2f}s")
            
            # Step 2: Run comprehensive evaluations if available
            session_evaluation_result = None
            model_evaluation_result = None
            session_eval_duration = 0.0
            model_eval_duration = 0.0
            
            if dynamodb_modeling_session and dynamodb_data_model:
                # Run session evaluation
                print("🔄 Running DSPy session evaluation...")
                session_eval_start = time.time()
                
                session_evaluation_result = self.dspy_engine.evaluate_session(scenario, dynamodb_modeling_session)
                session_eval_duration = time.time() - session_eval_start
                print(f"✅ Session evaluation completed in {session_eval_duration:.2f}s")
                print(f"📊 Session Score: {session_evaluation_result.overall_score:.2f} ({session_evaluation_result.quality_level})")
                
                # Run model evaluation
                print("🔄 Running DSPy model evaluation...")
                model_eval_start = time.time()
                
                model_evaluation_result = self.dspy_engine.evaluate_guidance(scenario, dynamodb_data_model)
                model_eval_duration = time.time() - model_eval_start
                print(f"✅ Model evaluation completed in {model_eval_duration:.2f}s")
                print(f"📊 Model Score: {model_evaluation_result.overall_score:.2f} ({model_evaluation_result.quality_level})")
            
            # Step 3: Create comprehensive result with separate evaluations
            result = ComprehensiveEvaluationResult(
                modeling_session=dynamodb_modeling_session or "",
                data_model=dynamodb_data_model or "",
                conversation=conversation,
                session_evaluation=session_evaluation_result,
                model_evaluation=model_evaluation_result,
                conversation_duration=conversation_duration,
                session_evaluation_duration=session_eval_duration,
                model_evaluation_duration=model_eval_duration,
                timestamp=self._get_timestamp(),
                session_quality_level=session_evaluation_result.quality_level if session_evaluation_result else "unknown",
                model_quality_level=model_evaluation_result.quality_level if model_evaluation_result else "unknown"
            )
                        
            total_duration = time.time() - start_time
            print(f"🎯 Complete evaluation finished in {total_duration:.2f}s")
            
            return result
            
        except Exception as e:
            print(f"❌ Error during enhanced evaluation: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def evaluate_scenarios(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhanced scenario evaluation with separate session and model assessments.
        
        Args:
            scenario: Complete scenario specification
            
        Returns:
            Dictionary with comprehensive evaluation results
        """
        result = asyncio.run(self.evaluate_with_conversation(scenario))
        
        if not result:
            return {
                "status": "error",
                "message": "Evaluation failed",
                "timestamp": self._get_timestamp()
            }
        
        return {
            "status": "success",
            "conversation": [
                {
                    "role": turn.role,
                    "content": turn.content,
                    "turn_number": turn.turn_number,
                    "timestamp": turn.timestamp
                } for turn in result.conversation
            ],
            "modeling_session": result.modeling_session,
            "data_model": result.data_model,
            "session_evaluation": self._session_evaluation_to_dict(result.session_evaluation) if result.session_evaluation else None,
            "model_evaluation": self._model_evaluation_to_dict(result.model_evaluation) if result.model_evaluation else None,
            "quality_assessment": {
                "session_quality_level": result.session_quality_level,
                "model_quality_level": result.model_quality_level,
            },
            "performance_metadata": {
                "conversation_duration": result.conversation_duration,
                "session_evaluation_duration": result.session_evaluation_duration,
                "model_evaluation_duration": result.model_evaluation_duration,
                "total_duration": result.conversation_duration + result.session_evaluation_duration + result.model_evaluation_duration,
            },
            "timestamp": result.timestamp
        }
        
    def _session_evaluation_to_dict(self, session_result: SessionEvaluationResult) -> Dict[str, Any]:
        """Convert SessionEvaluationResult to dictionary format."""
        return {
            "scores": {
                "requirements_engineering": session_result.requirements_engineering,
                "access_pattern_analysis": session_result.access_pattern_analysis,
                "methodology_adherence": session_result.methodology_adherence,
                "technical_reasoning": session_result.technical_reasoning,
                "process_documentation": session_result.process_documentation,
            },
            "overall_score": session_result.overall_score,
            "quality_level": session_result.quality_level,
            "justifications": session_result.justifications,
        }
    
    def _model_evaluation_to_dict(self, model_result: EvaluationResult) -> Dict[str, Any]:
        """Convert EvaluationResult to dictionary format."""
        return {
            "scores": {
                "completeness": model_result.completeness,
                "technical_accuracy": model_result.technical_accuracy,
                "access_pattern_coverage": model_result.access_pattern_coverage,
                "scalability_considerations": model_result.scalability_considerations,
                "cost_optimization": model_result.cost_optimization,
            },
            "overall_score": model_result.overall_score,
            "quality_level": model_result.quality_level,
            "justifications": model_result.justifications,
        }
    
    def _evaluation_to_dict(self, evaluation_result: EvaluationResult) -> Dict[str, Any]:
        """Convert EvaluationResult to dictionary format."""
        return {
            "scores": {
                "completeness": evaluation_result.completeness,
                "technical_accuracy": evaluation_result.technical_accuracy,
                "access_pattern_coverage": evaluation_result.access_pattern_coverage,
                "scalability_considerations": evaluation_result.scalability_considerations,
                "cost_optimization": evaluation_result.cost_optimization,
            },
            "overall_score": evaluation_result.overall_score,
            "quality_level": evaluation_result.quality_level,
            "justifications": evaluation_result.justifications,
            # "improvement_recommendations": evaluation_result.improvement_recommendations
        }
    
    def _get_timestamp(self) -> str:
        """Get current timestamp for tracking."""
        import datetime
        return datetime.datetime.now().isoformat()


# # Backward compatibility alias
class MultiTurnEvaluator(EnhancedMultiTurnEvaluator):
    """Backward compatibility alias for MultiTurnEvaluator."""
    pass
