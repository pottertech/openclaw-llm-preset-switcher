"""
OpenClaw LLM Preset Switcher v2.0
Execution Policy Module for Ecosystem Integration

Converts task classification into structured execution policy.
Works with: pg-memory, dynamic-skills, token-guardian, lobster
"""

from enum import Enum
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field


class TaskClass(Enum):
    """Task classification taxonomy."""
    SHELL = "shell"
    BROWSER = "browser"
    RAG = "rag"
    TROUBLESHOOTING = "troubleshooting"
    FILE_OPS = "file_ops"
    CREATIVE = "creative"
    PLANNING = "planning"
    MIXED = "mixed"
    UNKNOWN = "unknown"


class WorkflowPhase(Enum):
    """Lobster workflow phases."""
    DISCOVER = "discover"
    PLAN = "plan"
    EXECUTE = "execute"
    VERIFY = "verify"
    SUMMARIZE = "summarize"


class ModelFamily(Enum):
    """Supported model families."""
    KIMI = "kimi"
    DEEPSEEK = "deepseek"
    MINIMAX = "minimax"
    QWEN = "qwen"
    MISTRAL = "mistral"


class ExecutionRole(Enum):
    """Execution roles."""
    OPERATOR = "operator"
    RESEARCHER = "researcher"
    DEBUGGER = "debugger"
    CREATOR = "creator"
    PLANNER = "planner"


class ExecutionMode(Enum):
    """Execution modes with preset configurations."""
    OPERATIONAL = "operational"
    ANALYTICAL = "analytical"
    CREATIVE = "creative"


@dataclass
class TokenState:
    """Token budget state from token-guardian."""
    context_used: int = 0
    context_limit: int = 16000
    risk_level: str = "low"  # low, medium, high
    safe_max_tokens: int = 1200
    token_pressure: float = 0.0  # 0.0 - 1.0
    
    @property
    def is_high_pressure(self) -> bool:
        return self.token_pressure > 0.8 or self.risk_level == "high"
    
    @property
    def is_medium_pressure(self) -> bool:
        return 0.6 < self.token_pressure <= 0.8 or self.risk_level == "medium"


@dataclass
class MemoryContext:
    """Memory context from pg-memory."""
    prior_decisions: List[Dict] = field(default_factory=list)
    memory_tags: List[str] = field(default_factory=list)
    session_summary: str = ""
    relevant_memories: int = 0
    recurring_workflow: bool = False
    prior_troubleshooting: bool = False
    
    @property
    def has_relevant_context(self) -> bool:
        return self.relevant_memories > 0


@dataclass
class SkillCandidate:
    """Candidate skill from dynamic-skills."""
    skill_name: str
    confidence: float
    tool_types: List[str] = field(default_factory=list)
    

@dataclass
class PolicyInput:
    """Expanded input contract for policy decisions."""
    # Core inputs
    request_text: str = ""
    task_label: Optional[str] = None
    
    # Workflow context
    workflow_phase: Optional[str] = None
    
    # Memory context
    memory_context: Optional[MemoryContext] = None
    memory_tags: List[str] = field(default_factory=list)
    prior_decisions: List[Dict] = field(default_factory=list)
    
    # Skill context
    candidate_skills: List[SkillCandidate] = field(default_factory=list)
    candidate_skill_scores: Dict[str, float] = field(default_factory=dict)
    
    # Token context
    token_budget_state: Optional[TokenState] = None
    context_used: int = 0
    context_limit: int = 16000
    risk_level: str = "low"
    safe_max_tokens: int = 1200
    
    # Model context
    current_model: Optional[str] = None
    preferred_model_family: Optional[str] = None
    
    # Control flags
    approval_required: bool = False
    
    def to_dict(self) -> Dict:
        return {
            'request_text': self.request_text,
            'task_label': self.task_label,
            'workflow_phase': self.workflow_phase,
            'memory_tags': self.memory_tags,
            'prior_decisions_count': len(self.prior_decisions),
            'candidate_skills_count': len(self.candidate_skills),
            'context_used': self.context_used,
            'context_limit': self.context_limit,
            'risk_level': self.risk_level,
            'safe_max_tokens': self.safe_max_tokens,
            'current_model': self.current_model,
            'approval_required': self.approval_required
        }


@dataclass
class PolicyOutput:
    """Expanded output contract for execution policy."""
    # Schema
    schema_version: str = "2.0.0"
    
    # Classification
    task_class: str = "unknown"
    confidence: float = 0.5
    reason: str = ""
    
    # Execution guidance
    recommended_role: str = "planner"
    recommended_mode: str = "analytical"
    recommended_model_family: str = "kimi"
    reasoning_depth: str = "standard"  # shallow, standard, deep
    
    # Policies
    tool_policy: str = "auto"  # none, conservative, auto, aggressive
    context_priority: str = "balanced"  # tokens, context, balanced
    latency_priority: str = "balanced"  # speed, quality, balanced
    cost_priority: str = "balanced"  # cheap, quality, balanced
    
    # Budgets
    max_output_budget: int = 1200
    phase_hint: str = "plan"
    execution_style: str = "standard"  # careful, standard, aggressive
    
    # Quality gates
    verification_needed: bool = False
    approval_gate: bool = False
    
    # Skill guidance
    selected_candidate_skill: Optional[str] = None
    candidate_chain_hint: List[str] = field(default_factory=list)
    
    # Preset (legacy compatibility)
    role: str = "planner"
    mode: str = "analytical"
    temperature: float = 0.4
    top_p: float = 0.9
    max_tokens: int = 1200
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON output."""
        return {
            'schema_version': self.schema_version,
            'task_class': self.task_class,
            'confidence': round(self.confidence, 2),
            'reason': self.reason,
            'recommended_role': self.recommended_role,
            'recommended_mode': self.recommended_mode,
            'recommended_model_family': self.recommended_model_family,
            'reasoning_depth': self.reasoning_depth,
            'tool_policy': self.tool_policy,
            'context_priority': self.context_priority,
            'latency_priority': self.latency_priority,
            'cost_priority': self.cost_priority,
            'max_output_budget': self.max_output_budget,
            'phase_hint': self.phase_hint,
            'execution_style': self.execution_style,
            'verification_needed': self.verification_needed,
            'approval_gate': self.approval_gate,
            'selected_candidate_skill': self.selected_candidate_skill,
            'candidate_chain_hint': self.candidate_chain_hint,
            # Legacy preset fields
            'role': self.role,
            'mode': self.mode,
            'temperature': self.temperature,
            'top_p': self.top_p,
            'max_tokens': self.max_tokens
        }
