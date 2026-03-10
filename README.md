# OpenClaw LLM Preset Switcher

A lightweight helper tool and OpenClaw skill that classifies tasks and generates
recommended LLM execution presets.

This project does **not directly modify OpenClaw configuration**.

It:
1. Classifies the task
2. Selects a role and execution mode
3. Emits JSON presets that another tool or agent can apply.

---

## Purpose

Different tasks benefit from different LLM settings.

Examples:

| Task | Best Mode |
|-----|-----|
| shell operations | operational |
| browser automation | operational |
| research | analytical |
| debugging | analytical |
| creative writing | creative |

This tool standardizes those settings.

---

## Repo Structure

.
├── SKILL.md
├── README.md
└── bin
    └── generate_llm_preset.py

---

## Usage

Example:

python bin/generate_llm_preset.py shell

Example output:

{
 "role": "operator",
 "mode": "operational",
 "temperature": 0.2,
 "top_p": 0.9,
 "max_tokens": 1200
}

---

## Task Classes

shell
browser
rag
troubleshooting
file_ops
creative
planning

---

## Safety

This tool **never edits OpenClaw configuration automatically**.

The output JSON is intended to be consumed by another workflow or applied manually.
