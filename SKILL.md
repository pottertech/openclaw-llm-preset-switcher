---
name: openclaw-llm-preset-switcher
description: Execution policy engine that classifies tasks and generates LLM execution policies based on ecosystem signals (pg-memory, dynamic-skills, token-guardian).
version: 2.0.0
---

# OpenClaw LLM Preset Switcher

**Execution Policy Engine v2.0**

Converts task classification into structured execution policy, consuming signals from:
- **pg-memory** (context recall)
- **dynamic-skills** (skill candidates)
- **token-guardian** (token budgets)

And producing output for:
- **Lobster** (workflow orchestration)

## What It Does

1. **Classifies** natural language requests with confidence scoring
2. **Selects** execution role, mode, and model family
3. **Adjusts** for token pressure, memory context, and candidate skills
4. **Emits** structured policy JSON for downstream tools

## What It Does NOT Do

- ❌ Write OpenClaw config directly
- ❌ Execute skills itself
- ❌ Store long-term memory
- ❌ Manage token compaction
- ❌ Run workflows

## Usage

### Legacy (Backward Compatible)

```bash
python bin/generate_llm_preset.py shell
```

### Ecosystem-Aware (Recommended)

```bash
# From file
python bin/generate_llm_preset.py --input request.json

# From stdin
cat request.json | python bin/generate_llm_preset.py --json

# With explanation
python bin/generate_llm_preset.py shell --explain --pretty
```

## Input Contract

See `examples/full_ecosystem_input.json`:

- `request_text` - Natural language request
- `task_label` - Explicit task label (optional)
- `workflow_phase` - Phase hint (optional)
- `memory_context_summary` - Context from pg-memory
- `memory_tags` - Relevant tags
- `prior_decisions` - Previous decisions
- `candidate_skills` - Skills from dynamic-skills
- `token_budget_state` - Budget from token-guardian
- `current_model` - Current model info
- `approval_required` - Approval flag

## Output Contract

See `examples/full_ecosystem_output.json`:

- `schema_version` - Version string
- `task_class` - Classified task
- `confidence` - Classification confidence
- `reason` - Why this policy
- `recommended_role` - Execution role
- `recommended_mode` - Execution mode
- `recommended_model_family` - Model family
- `reasoning_depth` - shallow/standard/deep
- `tool_policy` - none/conservative/auto/aggressive
- `context_priority` - tokens/context/balanced
- `max_output_budget` - Token budget
- `phase_hint` - Workflow phase
- `execution_style` - careful/standard/aggressive
- `verification_needed` - Verification flag
- `selected_candidate_skill` - Top skill
- `candidate_chain_hint` - Skill sequence
- `role`/`mode`/`temperature`/`top_p`/`max_tokens` - Legacy fields

## Workflow Phases

| Phase | Reasoning | Output | Tools |
|-------|-----------|--------|-------|
| discover | medium | medium | conservative |
| plan | deep | large | auto |
| execute | shallow | tight | aggressive |
| verify | deep | medium | conservative |
| summarize | shallow | small | none |

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

## Integration Example

```python
# 1. pg-memory recall
memory_context = pg_memory.recall_similar(request)

# 2. dynamic-skills lookup
candidate_skills = dynamic_skills.find_matching(request)

# 3. token-guardian check
token_state = token_guardian.get_budget_state()

# 4. preset-switcher policy decision
input_payload = {
    "request_text": request,
    "memory_context_summary": memory_context.summary,
    "candidate_skills": candidate_skills,
    "token_budget_state": token_state
}

policy = preset_switcher.generate_policy(input_payload)

# 5. lobster execution
lobster.execute_with_policy(policy)

# 6. pg-memory writeback
pg_memory.store_result(result)
```

## CLI Options

- `task` - Task label (legacy mode)
- `--input FILE` - JSON file input
- `--json` - JSON from stdin
- `--phase PHASE` - Phase override
- `--explain` - Human-readable explanation
- `--pretty` - Pretty print JSON
- `--legacy` - Legacy format only

## Testing

```bash
python -m pytest tests/
```

## Migration from v1.0

- Legacy usage still works: `generate_llm_preset.py shell`
- New recommended: JSON input with ecosystem context
- See `examples/` for format

## Repository

https://github.com/pottertech/openclaw-llm-preset-switcher
