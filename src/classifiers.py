"""
Task Classification Module
Natural language request classification with confidence scoring.
"""

import re
from typing import Tuple, List, Dict, Optional
from schemas import TaskClass, WorkflowPhase


class TaskClassifier:
    """Classifies natural language requests into task classes."""
    
    # Keyword patterns for task detection
    PATTERNS = {
        TaskClass.SHELL: [
            r'\b(shell|bash|zsh|terminal|command|script|chmod|ls|cd|grep|awk|sed)\b',
            r'\b(run|execute|exec)\s+(command|script|shell)',
            r'\b(sudo|apt|yum|brew|npm|pip)\b',
        ],
        TaskClass.BROWSER: [
            r'\b(browser|chrome|firefox|web|website|url|navigate|click|scrape|crawl)\b',
            r'\b(selenium|playwright|puppeteer)\b',
            r'\b(open|visit|browse)\s+(site|page|url)\b',
        ],
        TaskClass.RAG: [
            r'\b(rag|retrieval|search|find|lookup|query|database|vector|embed)\b',
            r'\b(memory|recall|remember|past|previous|history)\b',
            r'\b(search|look up|find)\s+(for|the)?\b',
        ],
        TaskClass.TROUBLESHOOTING: [
            r'\b(debug|fix|repair|troubleshoot|diagnose|error|bug|issue|problem)\b',
            r'\b(not working|broken|failed|crash|exception)\b',
            r'\b(what went wrong|why is it|solve)\b',
        ],
        TaskClass.FILE_OPS: [
            r'\b(file|folder|directory|path|move|copy|delete|rename|create)\b',
            r'\b(read|write|edit|modify)\s+(file|config|json|yaml|text)\b',
        ],
        TaskClass.CREATIVE: [
            r'\b(write|create|generate|draft|compose|story|poem|blog|article|content)\b',
            r'\b(creative|imagine|design|brainstorm|ideate)\b',
        ],
        TaskClass.PLANNING: [
            r'\b(plan|design|architect|strategy|roadmap|approach|method)\b',
            r'\b(how should|what is the best way|suggest|recommend)\b',
        ],
    }
    
    # Mixed task indicators
    MIXED_INDICATORS = [
        r'\b(and then|after that|followed by|next|finally)\b',
        r'\b(first|second|third|step|phase|stage)\b',
        r'\b(summarize|summarise)\s+.*\s+(and|then)\s+(plan|create|write)',
        r'\b(find|search)\s+.*\s+(and|then)\s+(fix|debug|write)',
    ]
    
    @classmethod
    def classify(cls, request_text: str) -> Tuple[TaskClass, float, str]:
        """Classify a natural language request.
        
        Args:
            request_text: Natural language request
            
        Returns:
            Tuple of (task_class, confidence, reason)
        """
        if not request_text:
            return TaskClass.UNKNOWN, 0.0, "Empty request"
        
        request_lower = request_text.lower()
        scores = {}
        
        # Score each task class
        for task_class, patterns in cls.PATTERNS.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, request_lower, re.IGNORECASE))
                score += matches
            scores[task_class] = score
        
        # Check for mixed tasks
        mixed_score = sum(
            len(re.findall(pattern, request_lower, re.IGNORECASE))
            for pattern in cls.MIXED_INDICATORS
        )
        
        if mixed_score > 0 and len([s for s in scores.values() if s > 0]) > 1:
            # Multiple task types detected
            return TaskClass.MIXED, 0.7, f"Multiple task patterns detected (score: {mixed_score})"
        
        # Get best match
        if max(scores.values()) == 0:
            return TaskClass.UNKNOWN, 0.3, "No clear task pattern detected"
        
        best_task = max(scores, key=scores.get)
        best_score = scores[best_task]
        
        # Calculate confidence (0.5 to 1.0 based on score magnitude)
        confidence = min(0.5 + (best_score * 0.1), 0.95)
        
        # Generate reason
        matched_patterns = [
            p for p in cls.PATTERNS[best_task]
            if re.search(p, request_lower, re.IGNORECASE)
        ][:2]  # Top 2 patterns
        reason = f"Matched patterns: {', '.join(matched_patterns)}"
        
        return best_task, confidence, reason
    
    @classmethod
    def classify_with_fallback(
        cls,
        request_text: str,
        task_label: Optional[str] = None
    ) -> Tuple[TaskClass, float, str]:
        """Classify with explicit label fallback.
        
        Args:
            request_text: Natural language request
            task_label: Optional explicit label
            
        Returns:
            Tuple of (task_class, confidence, reason)
        """
        # Try natural language classification first
        task_class, confidence, reason = cls.classify(request_text)
        
        # If explicit label provided and high confidence, use it
        if task_label:
            label_map = {
                'shell': TaskClass.SHELL,
                'browser': TaskClass.BROWSER,
                'rag': TaskClass.RAG,
                'troubleshooting': TaskClass.TROUBLESHOOTING,
                'file_ops': TaskClass.FILE_OPS,
                'creative': TaskClass.CREATIVE,
                'planning': TaskClass.PLANNING,
            }
            
            if task_label in label_map:
                if confidence < 0.6:
                    # Explicit label overrides weak classification
                    return label_map[task_label], 0.8, f"Explicit label: {task_label}"
                else:
                    # Strong classification wins
                    return task_class, confidence, f"{reason} (label: {task_label})"
        
        return task_class, confidence, reason
    
    @classmethod
    def extract_subtasks(cls, request_text: str) -> List[Tuple[str, TaskClass]]:
        """Extract subtasks from mixed requests.
        
        Args:
            request_text: Natural language request
            
        Returns:
            List of (subtask_text, task_class) tuples
        """
        # Split by common delimiters
        parts = re.split(r'\b(and then|after that|followed by|next|finally|, then)\b', request_text, flags=re.IGNORECASE)
        
        subtasks = []
        for part in parts:
            part = part.strip()
            if len(part) > 10:  # Min meaningful length
                task_class, _, _ = cls.classify(part)
                if task_class != TaskClass.UNKNOWN:
                    subtasks.append((part, task_class))
        
        return subtasks if subtasks else [(request_text, TaskClass.UNKNOWN)]


class PhaseDetector:
    """Detects workflow phase from context."""
    
    PHASE_PATTERNS = {
        WorkflowPhase.DISCOVER: [
            r'\b(find|discover|explore|what is|identify|locate|search for)\b',
            r'\b(do we have|is there|are there)\b',
        ],
        WorkflowPhase.PLAN: [
            r'\b(plan|design|architect|strategy|approach|how to|best way)\b',
            r'\b(suggest|recommend|what should|need a plan)\b',
        ],
        WorkflowPhase.EXECUTE: [
            r'\b(run|execute|do|perform|implement|apply|make it)\b',
            r'\b(go ahead|proceed|carry out|complete)\b',
        ],
        WorkflowPhase.VERIFY: [
            r'\b(verify|check|test|validate|confirm|ensure|make sure)\b',
            r'\b(is it|does it|correct|working properly)\b',
        ],
        WorkflowPhase.SUMMARIZE: [
            r'\b(summarize|summarise|recap|review|condense|brief)\b',
            r'\b(tldr|key points|main takeaways|in short)\b',
        ],
    }
    
    @classmethod
    def detect(cls, request_text: str, memory_context: Optional[Dict] = None) -> Tuple[WorkflowPhase, str]:
        """Detect workflow phase.
        
        Args:
            request_text: Natural language request
            memory_context: Optional memory context
            
        Returns:
            Tuple of (phase, reason)
        """
        if not request_text:
            return WorkflowPhase.PLAN, "Default phase"
        
        request_lower = request_text.lower()
        
        # Score each phase
        for phase, patterns in cls.PHASE_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, request_lower, re.IGNORECASE):
                    return phase, f"Matched pattern: {pattern}"
        
        # Check memory context
        if memory_context:
            prior_decisions = memory_context.get('prior_decisions', [])
            if prior_decisions:
                # Have prior decisions → likely verify or execute
                if len(prior_decisions) > 2:
                    return WorkflowPhase.VERIFY, "Prior decisions suggest verification"
                return WorkflowPhase.EXECUTE, "Prior decisions suggest execution"
        
        # Default
        return WorkflowPhase.PLAN, "No clear phase detected"
