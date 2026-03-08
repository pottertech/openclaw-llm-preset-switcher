# OpenClaw LLM Preset Switcher v1.0.0

A custom OpenClaw skill that classifies a request by task type and recommends the best execution preset for the current turn.

This skill is built for operational reliability. It helps map requests into task classes such as shell, coding, RAG, browser, vision QC, creative prompting, planning, file operations, and troubleshooting.

## What it does

The skill classifies a request into:

- Task class
- Agent role
- Execution mode

It then guides the agent toward a safer and more effective response style for that task.

Examples:

- shell -> brodie -> strict
- coding -> coding -> balanced
- rag -> rag -> balanced
- browser -> brodie -> safe
- vision_qc -> vision -> balanced
- creative_prompting -> arty -> creative
- planning -> brodie -> balanced
- file_ops -> brodie -> safe
- troubleshooting -> brodie -> safe

## Included files

```text
SKILL.md
bin/generate_auto_preset.py
Install

Copy this folder into one of these OpenClaw skill locations:

~/.openclaw/skills/openclaw-llm-preset-switcher

or

<workspace>/skills/openclaw-llm-preset-switcher
Usage

The skill is intended to be available to OpenClaw during normal runs.

If your setup supports user-invocable skills, you can invoke it directly through the skill system.

The helper script can also generate provider-specific preset JSON.

Examples:

python3 bin/generate_auto_preset.py --provider ollama --task-class shell
python3 bin/generate_auto_preset.py --provider openai --task-class planning
python3 bin/generate_auto_preset.py --provider anthropic --task-class rag --tokens 1800
python3 bin/generate_auto_preset.py --provider gemini --task-class creative_prompting --mode creative
Supported providers

The helper script supports preset output for:

OpenAI-compatible

Ollama

Anthropic

Gemini

Notes

This skill does not automatically modify provider configuration on its own.

It guides model behavior for the current turn. If you want machine-readable preset JSON, use

the helper script.


