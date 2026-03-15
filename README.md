# 🦞 OpenClaw LLM Preset Switcher v2.0

**Execution Policy Engine for the OpenClaw Ecosystem**

Converts task requests into a structured execution policy, integrating with:
- **pg-memory** (context recall)
- **dynamic-skills** (skill candidates)
- **token-guardian** (token budgets)
- **lobster** (workflow orchestration)

> **Not a config mutator.** Emits policy JSON for other tools to consume.

---

## Purpose

This is an **execution policy engine**, not a static preset generator.

It consumes signals from across the OpenClaw ecosystem and produces:
- Task classification with confidence
- Execution role and mode recommendations
- Token-budget-aware output sizing
- Memory-informed phase selection
- Skill-aware tool policies
- Lobster-compatible workflow hints

---

## Quick Start

### Legacy Mode (Backward Compatible)

```bash
# Simple task label input
python bin/generate_llm_preset.py shell

# Output
{
  "role": "operator",
  "mode": "operational",
  "temperature": 0.2,
  "top_p": 0.9,
  "max_tokens": 1200
}
```

### Ecosystem-Aware Mode (Recommended)

```bash
# JSON file input
python bin/generate_llm_preset.py --input examples/full_ecosystem_input.json

# JSON from stdin
cat request.json | python bin/generate_llm_preset.py --json

# With explanation
python bin/generate_llm_preset.py shell --explain --pretty
```

---

## Integration Flow

Recommended execution order:

```
1. pg-memory → Recall relevant context
2. dynamic-skills → Lookup candidate skills
3. token-guardian → Check token budget
4. preset-switcher → Generate execution policy ← YOU ARE HERE
5. lobster → Orchestrate workflow
6. pg-memory → Store results
```

---

## Input Contract (v2.0)

```json
{
  "request_text": "Fix my nginx config",
  "task_label": "troubleshooting",
  "workflow_phase": "execute",
  "memory_context_summary": "Previous session...",
  "memory_tags": ["troubleshoot", "nginx"],
  "prior_decisions": [...],
  "candidate_skills": [
    {"name": "nginx-debug", "confidence": 0.92, "tool_types": ["shell"]}
  ],
  "token_budget_state": {
    "context_used": 8500,
    "context_limit": 16000,
    "risk_level": "medium",
    "safe_max_tokens": 3500
  },
  "current_model": "ollama/kimi-k2.5:cloud",
  "approval_required": false
}
```

---

## Output Contract (v2.0)

```json
{
  "schema_version": "2.0.0",
  "task_class": "troubleshooting",
  "confidence": 0.92,
  "reason": "Classification: matched debug patterns",
  
  "recommended_role": "debugger",
  "recommended_mode": "analytical",
  "recommended_model_family": "deepseek",
  "reasoning_depth": "shallow",
  
  "tool_policy": "conservative",
  "context_priority": "balanced",
  "latency_priority": "quality",
  "max_output_budget": 1400,
  
  "phase_hint": "execute",
  "execution_style": "careful",
  "verification_needed": true,
  
  "selected_candidate_skill": "nginx-debug",
  "candidate_chain_hint": ["nginx-debug", "web-verify"],
  
  "role": "debugger",
  "mode": "analytical",
  "temperature": 0.3,
  "top_p": 0.9,
  "max_tokens": 1600
}
```

---

## CLI Options

| Option | Description |
|--------|-------------|
| `task` | Task label (legacy): shell, browser, rag, etc. |
| `--input FILE` | Read JSON from file |
| `--json` | Read JSON from stdin |
| `--phase PHASE` | Override phase: discover, plan, execute, verify, summarize |
| `--explain` | Include human-readable explanation |
| `--pretty` | Pretty print JSON |
| `--legacy` | Output legacy format only |
| `--version` | Show version |

---

## What It Is (and Isn't)

### ✅ This Tool Does:
- **Consume** signals from pg-memory, dynamic-skills, token-guardian
- **Classify** natural language requests
- **Generate** execution policy recommendations
- **Output** structured JSON for other tools

### ❌ This Tool Does NOT:
- Write OpenClaw config directly
- Execute skills itself
- Store long-term memory
- Manage tokens or compaction
- Run workflows

---

## Repository Structure

```
.
├── bin/
│   └── generate_llm_preset.py    # CLI entrypoint
├── src/
│   ├── __init__.py
│   ├── schemas.py                # Input/output contracts
│   ├── classifiers.py           # Task classification
│   ├── policy_rules.py          # Policy logic
│   ├── adapters.py              # Input/output adapters
│   └── main.py                  # Policy engine
├── examples/
│   ├── simple_input.json        # Backward compatible
│   ├── full_ecosystem_input.json
│   └── full_ecosystem_output.json
├── tests/
│   └── test_policy_engine.py
├── SKILL.md
└── README.md
```

---

## Workflow Phases

| Phase | Characteristics |
|-------|-----------------|
| **discover** | Analytical, broad context, medium output |
| **plan** | Planner, structured output, deep reasoning |
| **execute** | Operational, tight output, tool-friendly |
| **verify** | Analytical, strict, concise |
| **summarize** | Concise, low token use |

---

## Task Classes

| Class | Role | Mode | Model |
|-------|------|------|-------|
| shell | operator | operational | minimax |
| browser | operator | operational | minimax |
| rag | researcher | analytical | kimi |
| troubleshooting | debugger | analytical | deepseek |
| file_ops | operator | operational | minimax |
| creative | creator | creative | qwen |
| planning | planner | analytical | kimi |

---

## Migration from v1.0

### What Changed

| v1.0 | v2.0 |
|------|------|
| Simple task label | Rich JSON input with ecosystem signals |
| 5-field output | Expanded policy with Lobster hints |
| Static presets | Dynamic policy based on token/memory/skill state |
| Standalone | Integrated with pg-memory, dynamic-skills, token-guardian |

### Backward Compatibility

Legacy usage still works:
```bash
python bin/generate_llm_preset.py shell
```

### New Recommended Usage

```bash
# Prepare ecosystem context
{
  "request_text": "Your request here",
  "memory_tags": ["relevant", "tags"],
  "candidate_skills": [...],
  "token_budget_state": {...}
} | python bin/generate_llm_preset.py --json
```

---

## Examples

### Example 1: Simple (Legacy)

```bash
$ python bin/generate_llm_preset.py shell
{
  "role": "operator",
  "mode": "operational",
  "temperature": 0.2,
  "top_p": 0.9,
  "max_tokens": 1200
}
```

### Example 2: Full Ecosystem Input

```bash
$ python bin/generate_llm_preset.py --input examples/full_ecosystem_input.json --pretty
```

Output:
```json
{
  "schema_version": "2.0.0",
  "task_class": "troubleshooting",
  "confidence": 0.92,
  "reason": "Classification: matched debug patterns",
  "recommended_role": "debugger",
  "recommended_mode": "analytical",
  "recommended_model_family": "deepseek",
  "reasoning_depth": "shallow",
  "tool_policy": "conservative",
  "context_priority": "balanced",
  "max_output_budget": 1400,
  "phase_hint": "execute",
  "execution_style": "careful",
  "verification_needed": true,
  "selected_candidate_skill": "nginx-debug",
  "candidate_chain_hint": ["nginx-debug", "web-verify"],
  "role": "debugger",
  "mode": "analytical",
  "temperature": 0.3,
  "top_p": 0.9,
  "max_tokens": 1600
}
```

### Example 3: With Explanation

```bash
$ python bin/generate_llm_preset.py rag --explain

Execution Policy (v2.0.0)
==================================================

Task Class: rag
Confidence: 85%
Reason: Classification: matched retrieval patterns; Phase: discover

Recommended:
  Role: researcher
  Mode: analytical
  Model Family: kimi
  Reasoning: medium

Policies:
  Tool Policy: auto
  Context Priority: context
  Max Output: 1600 tokens

Execution:
  Phase Hint: discover
  Style: careful
  Verification: No

==================================================
JSON Output:
==================================================
{...}
```

---

## Testing

```bash
# Run tests
python -m pytest tests/

# Test specific scenarios
python -m pytest tests/test_policy_engine.py -k "test_legacy"
```

---

## License

MIT
