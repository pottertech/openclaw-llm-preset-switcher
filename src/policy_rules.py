"""
Policy Rules Module
Deterministic rules for execution policy generation.
"""

from typing import Dict, Any, Optional
from schemas import (
    TaskClass, WorkflowPhase, ExecutionRole, ExecutionMode,
    TokenState, MemoryContext, PolicyInput, PolicyOutput
)


class PhasePolicy:
    """Policy rules for workflow phases."""
    
    @staticmethod
    def get_phase_policy(phase: WorkflowPhase) -> Dict[str, Any]:
        """Get policy for a workflow phase.
        
        Args:
            phase: Workflow phase
            
        Returns:
            Policy dictionary
        """
        policies = {
            WorkflowPhase.DISCOVER: {
                'reasoning_depth': 'medium',
                'context_priority': 'context',
                'latency_priority': 'quality',
                'max_output_budget': 1600,
                'execution_style': 'careful',
                'verification_needed': False,
                'tool_policy': 'conservative',
            },
            WorkflowPhase.PLAN: {
                'reasoning_depth': 'deep',
                'context_priority': 'balanced',
                'latency_priority': 'quality',
                'max_output_budget': 2000,
                'execution_style': 'careful',
                'verification_needed': True,
                'tool_policy': 'auto',
            },
            WorkflowPhase.EXECUTE: {
                'reasoning_depth': 'shallow',
                'context_priority': 'tokens',
                'latency_priority': 'speed',
                'max_output_budget': 1200,
                'execution_style': 'standard',
                'verification_needed': False,
                'tool_policy': 'aggressive',
            },
            WorkflowPhase.VERIFY: {
                'reasoning_depth': 'deep',
                'context_priority': 'balanced',
                'latency_priority': 'quality',
                'max_output_budget': 1400,
                'execution_style': 'careful',
                'verification_needed': True,
                'tool_policy': 'conservative',
            },
            WorkflowPhase.SUMMARIZE: {
                'reasoning_depth': 'shallow',
                'context_priority': 'tokens',
                'latency_priority': 'speed',
                'max_output_budget': 800,
                'execution_style': 'standard',
                'verification_needed': False,
                'tool_policy': 'none',
            },
        }
        
        return policies.get(phase, policies[WorkflowPhase.PLAN])


class TaskPolicy:
    """Policy rules for task classes."""
    
    TASK_MAPPINGS = {
        TaskClass.SHELL: {
            'role': ExecutionRole.OPERATOR,
            'mode': ExecutionMode.OPERATIONAL,
            'model_family': 'minimax',
            'temperature': 0.2,
            'max_tokens': 1200,
            'tool_policy': 'aggressive',
        },
        TaskClass.BROWSER: {
            'role': ExecutionRole.OPERATOR,
            'mode': ExecutionMode.OPERATIONAL,
            'model_family': 'minimax',
            'temperature': 0.2,
            'max_tokens': 1200,
            'tool_policy': 'aggressive',
        },
        TaskClass.RAG: {
            'role': ExecutionRole.RESEARCHER,
            'mode': ExecutionMode.ANALYTICAL,
            'model_family': 'kimi',
            'temperature': 0.4,
            'max_tokens': 1600,
            'tool_policy': 'auto',
        },
        TaskClass.TROUBLESHOOTING: {
            'role': ExecutionRole.DEBUGGER,
            'mode': ExecutionMode.ANALYTICAL,
            'model_family': 'deepseek',
            'temperature': 0.3,
            'max_tokens': 1600,
            'tool_policy': 'conservative',
        },
        TaskClass.FILE_OPS: {
            'role': ExecutionRole.OPERATOR,
            'mode': ExecutionMode.OPERATIONAL,
            'model_family': 'minimax',
            'temperature': 0.2,
            'max_tokens': 1200,
            'tool_policy': 'auto',
        },
        TaskClass.CREATIVE: {
            'role': ExecutionRole.CREATOR,
            'mode': ExecutionMode.CREATIVE,
            'model_family': 'qwen',
            'temperature': 0.8,
            'max_tokens': 2000,
            'tool_policy': 'none',
        },
        TaskClass.PLANNING: {
            'role': ExecutionRole.PLANNER,
            'mode': ExecutionMode.ANALYTICAL,
            'model_family': 'kimi',
            'temperature': 0.4,
            'max_tokens': 2000,
            'tool_policy': 'auto',
        },
        TaskClass.UNKNOWN: {
            'role': ExecutionRole.PLANNER,
            'mode': ExecutionMode.ANALYTICAL,
            'model_family': 'kimi',
            'temperature': 0.4,
            'max_tokens': 1600,
            'tool_policy': 'auto',
        },
    }
    
    @classmethod
    def get_task_policy(cls, task_class: TaskClass) -> Dict[str, Any]:
        """Get policy for a task class.
        
        Args:
            task_class: Task classification
            
        Returns:
            Policy dictionary
        """
        return cls.TASK_MAPPINGS.get(task_class, cls.TASK_MAPPINGS[TaskClass.UNKNOWN])


class TokenPressurePolicy:
    """Policy adjustments based on token pressure."""
    
    @staticmethod
    def adjust_for_token_pressure(
        base_policy: Dict[str, Any],
        token_state: TokenState
    ) -> Dict[str, Any]:
        """Adjust policy based on token pressure.
        
        Args:
            base_policy: Base policy
            token_state: Token budget state
            
        Returns:
            Adjusted policy
        """
        policy = base_policy.copy()
        
        if token_state.is_high_pressure:
            # High pressure: aggressive reductions
            policy['reasoning_depth'] = 'shallow'
            policy['max_output_budget'] = min(
                policy.get('max_output_budget', 1200),
                token_state.safe_max_tokens,
                800
            )
            policy['execution_style'] = 'careful'
            policy['tool_policy'] = 'conservative'
            policy['context_priority'] = 'tokens'
            policy['latency_priority'] = 'speed'
            policy['reason'] = f"High token pressure ({token_state.token_pressure:.1%})"
            
        elif token_state.is_medium_pressure:
            # Medium pressure: moderate reductions
            policy['reasoning_depth'] = 'shallow'
            policy['max_output_budget'] = min(
                policy.get('max_output_budget', 1200),
                token_state.safe_max_tokens
            )
            policy['execution_style'] = 'standard'
            policy['reason'] = f"Medium token pressure ({token_state.token_pressure:.1%})"
            
        return policy


class MemoryInformedPolicy:
    """Policy adjustments based on memory context."""
    
    @staticmethod
    def adjust_for_memory(
        base_policy: Dict[str, Any],
        memory_context: Optional[MemoryContext]
    ) -> Dict[str, Any]:
        """Adjust policy based on memory context.
        
        Args:
            base_policy: Base policy
            memory_context: Memory context from pg-memory
            
        Returns:
            Adjusted policy
        """
        if not memory_context:
            return base_policy
        
        policy = base_policy.copy()
        
        # Prior decisions exist → bias toward planning/verification
        if memory_context.prior_decisions:
            if len(memory_context.prior_decisions) > 2:
                policy['verification_needed'] = True
                policy['phase_hint'] = 'verify'
                policy['reason'] = f"{len(memory_context.prior_decisions)} prior decisions"
        
        # Recurring workflow → known pattern
        if memory_context.recurring_workflow:
            policy['execution_style'] = 'standard'
            policy['verification_needed'] = False
            policy['reason'] = "Recurring workflow pattern"
        
        # Prior troubleshooting → troubleshooting mode
        if memory_context.prior_troubleshooting:
            policy['reasoning_depth'] = 'deep'
            policy['tool_policy'] = 'conservative'
            policy['reason'] = "Prior troubleshooting context"
        
        # Sparse memory → allow exploration
        if not memory_context.has_relevant_context:
            policy['reasoning_depth'] = 'medium'
            policy['execution_style'] = 'careful'
            policy['reason'] = "Sparse memory context"
        
        return policy


class SkillAwarePolicy:
    """Policy adjustments based on candidate skills."""
    
    SKILL_TOOL_MAPPINGS = {
        'shell': ['bash', 'exec', 'run'],
        'browser': ['browser', 'web', 'navigate'],
        'rag': ['search', 'memory', 'retrieve'],
        'file': ['file', 'read', 'write'],
    }
    
    @classmethod
    def adjust_for_skills(
        cls,
        base_policy: Dict[str, Any],
        candidate_skills: list
    ) -> Dict[str, Any]:
        """Adjust policy based on candidate skills.
        
        Args:
            base_policy: Base policy
            candidate_skills: List of SkillCandidate
            
        Returns:
            Adjusted policy
        """
        if not candidate_skills:
            return base_policy
        
        policy = base_policy.copy()
        
        # Sort by confidence
        sorted_skills = sorted(
            candidate_skills,
            key=lambda s: s.confidence,
            reverse=True
        )
        
        # Top skill
        top_skill = sorted_skills[0]
        
        if top_skill.confidence > 0.7:
            policy['selected_candidate_skill'] = top_skill.skill_name
            policy['reason'] = f"Strong skill match: {top_skill.skill_name}"
            
            # Operational skills → operational mode
            if any(t in ['shell', 'browser', 'file'] for t in top_skill.tool_types):
                policy['mode'] = 'operational'
                policy['tool_policy'] = 'aggressive'
            
            # Analytical skills → analytical mode
            if any(t in ['rag', 'diagnosis', 'research'] for t in top_skill.tool_types):
                policy['mode'] = 'analytical'
                policy['reasoning_depth'] = 'deep'
            
            # Multiple skills → chain hint
            if len(sorted_skills) > 1 and sorted_skills[1].confidence > 0.5:
                policy['candidate_chain_hint'] = [
                    s.skill_name for s in sorted_skills[:3]
                ]
        
        # No strong skill → planning mode
        elif top_skill.confidence < 0.4:
            policy['phase_hint'] = 'plan'
            policy['reasoning_depth'] = 'deep'
            policy['reason'] = "No strong skill match"
        
        return policy


class PolicyMerger:
    """Merges multiple policy sources into final output."""
    
    @staticmethod
    def merge_policies(policies: list, priority_order: list = None) -> Dict[str, Any]:
        """Merge multiple policy dictionaries.
        
        Later policies override earlier ones unless in priority_order.
        
        Args:
            policies: List of policy dicts
            priority_order: Keys that should keep first value
            
        Returns:
            Merged policy
        """
        if not policies:
            return {}
        
        priority_order = priority_order or []
        result = {}
        
        # Apply policies in order
        for policy in policies:
            for key, value in policy.items():
                # Priority keys keep first value
                if key in priority_order and key in result:
                    continue
                result[key] = value
        
        return result
    
    @staticmethod
    def resolve_conflicts(policy: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve conflicting policy settings.
        
        Args:
            policy: Policy dictionary
            
        Returns:
            Resolved policy
        """
        resolved = policy.copy()
        
        # Conflict: shallow reasoning + aggressive tools
        if (resolved.get('reasoning_depth') == 'shallow' and
            resolved.get('tool_policy') == 'aggressive'):
            resolved['tool_policy'] = 'auto'
            resolved['resolution_note'] = 'Reduced tool aggression for shallow reasoning'
        
        # Conflict: creative mode + low tokens
        if (resolved.get('mode') == 'creative' and
            resolved.get('max_output_budget', 0) < 1000):
            resolved['mode'] = 'analytical'
            resolved['resolution_note'] = 'Switched from creative to analytical (token constraints)'
        
        return resolved
