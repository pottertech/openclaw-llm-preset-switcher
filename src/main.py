#!/usr/bin/env python3
"""
OpenClaw LLM Preset Switcher v2.0
Main entrypoint - Execution Policy Engine

Converts task classification into structured execution policy.
Works with: pg-memory, dynamic-skills, token-guardian, lobster
"""

import sys
from typing import Optional, Tuple

from schemas import (
    PolicyInput, PolicyOutput, TaskClass, WorkflowPhase,
    ExecutionRole, ExecutionMode, TokenState, MemoryContext
)
from classifiers import TaskClassifier, PhaseDetector
from policy_rules import (
    PhasePolicy, TaskPolicy, TokenPressurePolicy,
    MemoryInformedPolicy, SkillAwarePolicy, PolicyMerger
)
from adapters import InputAdapter, OutputAdapter, CLIParser


class PolicyEngine:
    """Main execution policy engine."""
    
    def __init__(self):
        """Initialize policy engine."""
        self.classifier = TaskClassifier()
        self.phase_detector = PhaseDetector()
    
    def generate_policy(self, policy_input: PolicyInput) -> PolicyOutput:
        """Generate execution policy from input.
        
        This is the main orchestration method that:
        1. Classifies the task
        2. Detects workflow phase
        3. Applies phase policy
        4. Applies task policy
        5. Adjusts for token pressure
        6. Adjusts for memory context
        7. Adjusts for candidate skills
        8. Merges and resolves conflicts
        
        Args:
            policy_input: Structured policy input
            
        Returns:
            PolicyOutput with execution recommendations
        """
        # Step 1: Classify task
        task_class, confidence, classification_reason = \
            TaskClassifier.classify_with_fallback(
                policy_input.request_text,
                policy_input.task_label
            )
        
        # Step 2: Detect phase
        phase, phase_reason = self.phase_detector.detect(
            policy_input.request_text,
            policy_input.memory_context.to_dict() if policy_input.memory_context else None
        )
        
        # Step 3: Get phase policy
        phase_policy = PhasePolicy.get_phase_policy(phase)
        
        # Step 4: Get task policy
        task_policy = TaskPolicy.get_task_policy(task_class)
        
        # Step 5: Apply token pressure adjustments
        token_adjusted = task_policy.copy()
        if policy_input.token_budget_state:
            token_adjusted = TokenPressurePolicy.adjust_for_token_pressure(
                task_policy,
                policy_input.token_budget_state
            )
        else:
            # Create token state from direct fields
            token_state = TokenState(
                context_used=policy_input.context_used,
                context_limit=policy_input.context_limit,
                risk_level=policy_input.risk_level,
                safe_max_tokens=policy_input.safe_max_tokens
            )
            token_adjusted = TokenPressurePolicy.adjust_for_token_pressure(
                task_policy,
                token_state
            )
        
        # Step 6: Apply memory-informed adjustments
        memory_adjusted = token_adjusted.copy()
        if policy_input.memory_context:
            memory_adjusted = MemoryInformedPolicy.adjust_for_memory(
                token_adjusted,
                policy_input.memory_context
            )
        
        # Step 7: Apply skill-aware adjustments
        skill_adjusted = memory_adjusted.copy()
        if policy_input.candidate_skills:
            skill_adjusted = SkillAwarePolicy.adjust_for_skills(
                memory_adjusted,
                policy_input.candidate_skills
            )
        
        # Step 8: Merge all policies
        # Priority: task_policy < phase_policy < adjustments
        merged = PolicyMerger.merge_policies([
            task_policy,
            phase_policy,
            token_adjusted,
            memory_adjusted,
            skill_adjusted
        ])
        
        # Step 9: Resolve conflicts
        final_policy = PolicyMerger.resolve_conflicts(merged)
        
        # Build output
        return PolicyOutput(
            schema_version="2.0.0",
            task_class=task_class.value,
            confidence=confidence,
            reason=self._build_reason(
                classification_reason,
                phase_reason,
                final_policy.get('reason', '')
            ),
            recommended_role=final_policy.get('role', 'planner'),
            recommended_mode=final_policy.get('mode', 'analytical'),
            recommended_model_family=final_policy.get('model_family', 'kimi'),
            reasoning_depth=final_policy.get('reasoning_depth', 'standard'),
            tool_policy=final_policy.get('tool_policy', 'auto'),
            context_priority=final_policy.get('context_priority', 'balanced'),
            latency_priority=final_policy.get('latency_priority', 'balanced'),
            cost_priority=final_policy.get('cost_priority', 'balanced'),
            max_output_budget=final_policy.get('max_output_budget', 1200),
            phase_hint=final_policy.get('phase_hint', phase.value),
            execution_style=final_policy.get('execution_style', 'standard'),
            verification_needed=final_policy.get('verification_needed', False),
            approval_gate=policy_input.approval_required or final_policy.get('approval_gate', False),
            selected_candidate_skill=final_policy.get('selected_candidate_skill'),
            candidate_chain_hint=final_policy.get('candidate_chain_hint', []),
            # Legacy fields
            role=final_policy.get('role', 'planner'),
            mode=final_policy.get('mode', 'analytical'),
            temperature=final_policy.get('temperature', 0.4),
            top_p=final_policy.get('top_p', 0.9),
            max_tokens=final_policy.get('max_tokens', 1200)
        )
    
    def _build_reason(self, classification: str, phase: str, adjustment: str) -> str:
        """Build composite reason string.
        
        Args:
            classification: Classification reason
            phase: Phase detection reason
            adjustment: Adjustment reason
            
        Returns:
            Composite reason
        """
        parts = []
        if classification:
            parts.append(f"Classification: {classification}")
        if phase:
            parts.append(f"Phase: {phase}")
        if adjustment:
            parts.append(f"Adjustment: {adjustment}")
        return "; ".join(parts) if parts else "Default policy"


def main():
    """Main CLI entrypoint."""
    # Parse arguments
    args = CLIParser.parse()
    
    # Validate
    is_valid, error = CLIParser.validate(args)
    if not is_valid:
        print(f"Error: {error}", file=sys.stderr)
        print("\nUse --help for usage information", file=sys.stderr)
        sys.exit(1)
    
    # Build input
    policy_input = None
    input_error = None
    
    if args.json:
        # Read from stdin
        policy_input, input_error = InputAdapter.from_stdin()
    elif args.input:
        # Read from file
        policy_input, input_error = InputAdapter.from_json_file(args.input)
    else:
        # Legacy CLI mode
        policy_input = InputAdapter.from_legacy_args([args.task] if args.task else [])
    
    if input_error:
        # Create fallback input with error reason
        policy_input = PolicyInput(
            request_text=args.task or '',
            task_label=args.task,
        )
        print(f"Warning: {input_error}", file=sys.stderr)
        print("Falling back to basic policy generation.\n", file=sys.stderr)
    
    # Override phase if specified
    if args.phase:
        policy_input.workflow_phase = args.phase
    
    # Generate policy
    engine = PolicyEngine()
    policy_output = engine.generate_policy(policy_input)
    
    # Output results
    if args.explain:
        # Human-readable explanation
        print(OutputAdapter.to_explanation(policy_output))
        print("\n" + "=" * 50)
        print("JSON Output:")
        print("=" * 50)
    
    if args.legacy:
        # Legacy format only
        print(OutputAdapter.to_legacy_format(policy_output))
    else:
        # Full v2.0 format
        print(OutputAdapter.to_json(policy_output, pretty=args.pretty))


if __name__ == '__main__':
    main()
