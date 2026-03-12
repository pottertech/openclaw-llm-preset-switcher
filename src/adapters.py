"""
Input/Output Adapters
Handles CLI, JSON file, and stdin input formats.
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Optional, Dict, Any, Tuple

from schemas import PolicyInput, PolicyOutput, TokenState, MemoryContext, SkillCandidate
from classifiers import TaskClassifier, PhaseDetector


class InputAdapter:
    """Adapts various input formats to PolicyInput."""
    
    @staticmethod
    def from_legacy_args(args: list) -> PolicyInput:
        """Parse legacy CLI arguments.
        
        Args:
            args: CLI arguments list
            
        Returns:
            PolicyInput
        """
        task_label = args[0] if args else None
        
        return PolicyInput(
            request_text=' '.join(args) if args else '',
            task_label=task_label,
            workflow_phase=None,
        )
    
    @staticmethod
    def from_json_file(filepath: str) -> Tuple[PolicyInput, Optional[str]]:
        """Parse JSON file input.
        
        Args:
            filepath: Path to JSON file
            
        Returns:
            Tuple of (PolicyInput, error_message)
        """
        try:
            path = Path(filepath)
            if not path.exists():
                return PolicyInput(), f"File not found: {filepath}"
            
            with open(path) as f:
                data = json.load(f)
            
            return InputAdapter._from_dict(data), None
            
        except json.JSONDecodeError as e:
            return PolicyInput(), f"Invalid JSON: {e}"
        except Exception as e:
            return PolicyInput(), f"Error reading file: {e}"
    
    @staticmethod
    def from_stdin() -> Tuple[PolicyInput, Optional[str]]:
        """Parse JSON from stdin.
        
        Returns:
            Tuple of (PolicyInput, error_message)
        """
        try:
            data = json.load(sys.stdin)
            return InputAdapter._from_dict(data), None
        except json.JSONDecodeError as e:
            return PolicyInput(), f"Invalid JSON from stdin: {e}"
        except Exception as e:
            return PolicyInput(), f"Error reading stdin: {e}"
    
    @staticmethod
    def _from_dict(data: Dict[str, Any]) -> PolicyInput:
        """Convert dictionary to PolicyInput.
        
        Args:
            data: Input dictionary
            
        Returns:
            PolicyInput
        """
        # Build TokenState
        token_state = None
        if 'token_budget_state' in data:
            token_data = data['token_budget_state']
            token_state = TokenState(
                context_used=token_data.get('context_used', 0),
                context_limit=token_data.get('context_limit', 16000),
                risk_level=token_data.get('risk_level', 'low'),
                safe_max_tokens=token_data.get('safe_max_tokens', 1200),
                token_pressure=token_data.get('token_pressure', 0.0)
            )
        elif any(k in data for k in ['context_used', 'context_limit', 'risk_level']):
            token_state = TokenState(
                context_used=data.get('context_used', 0),
                context_limit=data.get('context_limit', 16000),
                risk_level=data.get('risk_level', 'low'),
                safe_max_tokens=data.get('safe_max_tokens', 1200)
            )
        
        # Build MemoryContext
        memory_context = None
        if 'memory_context_summary' in data or 'prior_decisions' in data:
            memory_context = MemoryContext(
                session_summary=data.get('memory_context_summary', ''),
                prior_decisions=data.get('prior_decisions', []),
                memory_tags=data.get('memory_tags', []),
                recurring_workflow=any(t in data.get('memory_tags', []) 
                                        for t in ['recurring', 'workflow', 'pattern']),
                prior_troubleshooting=any(t in data.get('memory_tags', [])
                                         for t in ['troubleshoot', 'debug', 'fix'])
            )
        
        # Build SkillCandidates
        candidate_skills = []
        if 'candidate_skills' in data:
            for skill in data['candidate_skills']:
                candidate_skills.append(SkillCandidate(
                    skill_name=skill.get('name', skill.get('skill_name', 'unknown')),
                    confidence=skill.get('confidence', 0.5),
                    tool_types=skill.get('tool_types', [])
                ))
        
        return PolicyInput(
            request_text=data.get('request_text', ''),
            task_label=data.get('task_label'),
            workflow_phase=data.get('workflow_phase'),
            memory_context=memory_context,
            memory_tags=data.get('memory_tags', []),
            prior_decisions=data.get('prior_decisions', []),
            candidate_skills=candidate_skills,
            candidate_skill_scores=data.get('candidate_skill_scores', {}),
            token_budget_state=token_state,
            context_used=data.get('context_used', 0),
            context_limit=data.get('context_limit', 16000),
            risk_level=data.get('risk_level', 'low'),
            safe_max_tokens=data.get('safe_max_tokens', 1200),
            current_model=data.get('current_model'),
            preferred_model_family=data.get('preferred_model_family'),
            approval_required=data.get('approval_required', False)
        )


class OutputAdapter:
    """Adapts PolicyOutput to various output formats."""
    
    @staticmethod
    def to_json(output: PolicyOutput, pretty: bool = False) -> str:
        """Convert output to JSON string.
        
        Args:
            output: PolicyOutput
            pretty: Pretty print if True
            
        Returns:
            JSON string
        """
        data = output.to_dict()
        
        if pretty:
            return json.dumps(data, indent=2)
        return json.dumps(data)
    
    @staticmethod
    def to_legacy_format(output: PolicyOutput) -> str:
        """Convert to legacy format for backward compatibility.
        
        Args:
            output: PolicyOutput
            
        Returns:
            Legacy JSON string
        """
        legacy = {
            'role': output.role,
            'mode': output.mode,
            'temperature': output.temperature,
            'top_p': output.top_p,
            'max_tokens': output.max_tokens
        }
        return json.dumps(legacy, indent=2)
    
    @staticmethod
    def to_explanation(output: PolicyOutput) -> str:
        """Generate human-readable explanation.
        
        Args:
            output: PolicyOutput
            
        Returns:
            Explanation text
        """
        lines = [
            f"Execution Policy (v{output.schema_version})",
            "=" * 50,
            f"",
            f"Task Class: {output.task_class}",
            f"Confidence: {output.confidence:.0%}",
            f"Reason: {output.reason}",
            f"",
            f"Recommended:",
            f"  Role: {output.recommended_role}",
            f"  Mode: {output.recommended_mode}",
            f"  Model Family: {output.recommended_model_family}",
            f"  Reasoning: {output.reasoning_depth}",
            f"",
            f"Policies:",
            f"  Tool Policy: {output.tool_policy}",
            f"  Context Priority: {output.context_priority}",
            f"  Latency Priority: {output.latency_priority}",
            f"  Max Output: {output.max_output_budget} tokens",
            f"",
            f"Execution:",
            f"  Phase Hint: {output.phase_hint}",
            f"  Style: {output.execution_style}",
            f"  Verification: {'Yes' if output.verification_needed else 'No'}",
        ]
        
        if output.selected_candidate_skill:
            lines.append(f"  Selected Skill: {output.selected_candidate_skill}")
        
        if output.candidate_chain_hint:
            lines.append(f"  Skill Chain: {' → '.join(output.candidate_chain_hint)}")
        
        return '\n'.join(lines)


class CLIParser:
    """Command-line argument parser."""
    
    @staticmethod
    def parse(args: Optional[list] = None) -> argparse.Namespace:
        """Parse command-line arguments.
        
        Args:
            args: Arguments list (defaults to sys.argv[1:])
            
        Returns:
            Parsed namespace
        """
        parser = argparse.ArgumentParser(
            prog='generate_llm_preset',
            description='OpenClaw LLM Preset Switcher - Execution Policy Engine',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  # Legacy mode
  generate_llm_preset shell
  
  # JSON file input
  generate_llm_preset --input request.json
  
  # JSON from stdin
  cat request.json | generate_llm_preset --json
  
  # With explanation
  generate_llm_preset shell --explain --pretty
            """
        )
        
        # Input options
        input_group = parser.add_mutually_exclusive_group()
        input_group.add_argument(
            'task',
            nargs='?',
            help='Task label (legacy mode): shell, browser, rag, etc.'
        )
        input_group.add_argument(
            '--input', '-i',
            metavar='FILE',
            help='Read request from JSON file'
        )
        input_group.add_argument(
            '--json', '-j',
            action='store_true',
            help='Read JSON from stdin'
        )
        
        # Phase override
        parser.add_argument(
            '--phase',
            choices=['discover', 'plan', 'execute', 'verify', 'summarize'],
            help='Override workflow phase'
        )
        
        # Output options
        parser.add_argument(
            '--explain', '-e',
            action='store_true',
            help='Include human-readable explanation'
        )
        parser.add_argument(
            '--pretty', '-p',
            action='store_true',
            help='Pretty print JSON output'
        )
        parser.add_argument(
            '--legacy',
            action='store_true',
            help='Output legacy format only'
        )
        
        # Other options
        parser.add_argument(
            '--version', '-v',
            action='version',
            version='%(prog)s 2.0.0'
        )
        
        return parser.parse_args(args)
    
    @staticmethod
    def validate(args: argparse.Namespace) -> Tuple[bool, Optional[str]]:
        """Validate parsed arguments.
        
        Args:
            args: Parsed namespace
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Must have some input
        if not args.task and not args.input and not args.json:
            return False, "No input provided. Use task label, --input, or --json"
        
        # Validate file exists
        if args.input and not Path(args.input).exists():
            return False, f"Input file not found: {args.input}"
        
        return True, None
