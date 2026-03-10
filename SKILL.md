# OpenClaw LLM Preset Switcher Skill

This skill classifies tasks and recommends LLM execution presets.

It does not directly modify configuration.

---

## Task Mapping

shell → operator / operational
browser → operator / operational
rag → researcher / analytical
troubleshooting → debugger / analytical
file_ops → operator / operational
creative → creator / creative
planning → planner / analytical

---

## Modes

Operational
Low temperature, deterministic responses.

Analytical
Balanced reasoning and accuracy.

Creative
Higher temperature and broader generation.

---

## Output

The preset generator emits JSON:

role
mode
temperature
top_p
max_tokens

Downstream tools may translate these into provider‑specific settings.
