# Migration Guide: v1.0 → v2.0

## What Changed

### Input

**v1.0:** Simple task label
```bash
generate_llm_preset.py shell
```

**v2.0:** Rich ecosystem-aware JSON
```json
{
  "request_text": "Fix nginx config",
  "memory_tags": ["troubleshoot"],
  "candidate_skills": [...],
  "token_budget_state": {...}
}
```

### Output

**v1.0:** 5-field legacy format
```json
{
  "role": "operator",
  "mode": "operational",
  "temperature": 0.2,
  "top_p": 0.9,
  "max_tokens": 1200
}
```

**v2.0:** Expanded policy with ecosystem hints
```json
{
  "schema_version": "2.0.0",
  "task_class": "troubleshooting",
  "confidence": 0.92,
  "reason": "...",
  "recommended_role": "debugger",
  "recommended_mode": "analytical",
  "reasoning_depth": "shallow",
  "tool_policy": "conservative",
  "max_output_budget": 1400,
  "phase_hint": "execute",
  "verification_needed": true,
  "selected_candidate_skill": "nginx-debug",
  "candidate_chain_hint": [...],
  "role": "debugger",  // legacy compatibility
  "mode": "analytical",
  "temperature": 0.3,
  "top_p": 0.9,
  "max_tokens": 1600
}
```

## Backward Compatibility

Legacy usage **still works**:

```bash
generate_llm_preset.py shell
# Output: legacy format with v2.0 logic
```

Use `--legacy` flag for strict v1.0 output.

## New Recommended Usage

### 1. Simple Ecosystem Input

```bash
cat <<EOF | generate_llm_preset.py --json --pretty
{
  "request_text": "Fix nginx config",
  "task_label": "troubleshooting"
}
EOF
```

### 2. Full Ecosystem Input

```bash
cat <<EOF | generate_llm_preset.py --json --pretty
{
  "request_text": "Fix nginx config and verify",
  "task_label": "troubleshooting",
  "memory_tags": ["troubleshoot", "nginx"],
  "prior_decisions": [{"decision": "Check syntax first"}],
  "candidate_skills": [
    {"name": "nginx-debug", "confidence": 0.92}
  ],
  "token_budget_state": {
    "context_used": 8500,
    "context_limit": 16000,
    "risk_level": "medium"
  }
}
EOF
```

### 3. With Explanation

```bash
generate_llm_preset.py shell --explain --pretty
```

## Code Changes

| Component | v1.0 | v2.0 |
|-----------|------|------|
| Architecture | Single script | Modular (src/) |
| Classification | Fixed labels | Natural language + confidence |
| Policy | Static | Dynamic (token/memory/skill aware) |
| Phases | None | discover/plan/execute/verify/summarize |
| Integration | Standalone | Ecosystem-aware |

## Files Added

- `src/schemas.py` - Input/output contracts
- `src/classifiers.py` - Task classification
- `src/policy_rules.py` - Policy logic
- `src/adapters.py` - Input/output adapters
- `src/main.py` - Policy engine
- `examples/` - Example inputs/outputs
- `tests/` - Test suite

## Breaking Changes

None for CLI usage.

For programmatic usage:
- Import path changed: `from main import PolicyEngine`
- Method signature: `generate_policy(input: PolicyInput)`
- Return type: `PolicyOutput` (has `.to_dict()` method)

## Integration Flow

```
v1.0: Task Label → Preset

v2.0: Request
       ↓
  pg-memory (recall)
       ↓
  dynamic-skills (candidates)
       ↓
  token-guardian (budget)
       ↓
  preset-switcher (policy) ← YOU ARE HERE
       ↓
  lobster (execution)
       ↓
  pg-memory (store)
```

See `examples/` for complete examples.
