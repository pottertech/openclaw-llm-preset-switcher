---
name: openclaw-auto-preset-switcher
description: Classify the current task and apply the recommended LLM preset strategy for Brodie, Arty, coding, RAG, browser, shell, vision QC, planning, and creative prompting work.
version: 1.0.0
author: Skip Potter
user-invocable: true
---

# OpenClaw Auto Preset Switcher

## Purpose

Use this skill to classify the current request into a task class, assign the best agent role behavior, and recommend the safest and most effective LLM preset profile for the work.

This skill does not directly change provider configuration by itself.
It guides the agent's reasoning and execution style for the current turn.
If a helper script is available in this skill folder, the agent may run it to emit ready-to-use JSON preset output.

## When to use this skill

Use this skill when the request involves any of these task classes:

- shell
- coding
- rag
- browser
- vision_qc
- creative_prompting
- planning
- file_ops
- troubleshooting

Use this skill only when task classification or preset selection would materially improve reliability, safety, or output quality.

## Operating rule

Follow this sequence exactly:

1. Identify the primary task class.
2. Identify the most likely agent role.
3. Select the recommended mode.
4. Apply the execution rules for that class.
5. Prefer first-class OpenClaw tools when available.
6. Only emit or run preset JSON when the user asks for it or when a downstream config step clearly needs it.

OpenClaw exposes first-class tools for browser, nodes, cron, and related workflows, and those should be preferred over older shell-based patterns when available.

## Task classification

Classify the request into exactly one primary task class:

### shell
Use for:
- terminal commands
- service control
- logs
- environment variables
- package installs
- file permissions
- launchd, systemd, cron, docker, ssh, mqtt, ollama, gateway, node, python runtime issues

Signals:
- "fix"
- "restart"
- "service"
- "logs"
- "launchagent"
- "gateway"
- "unauthorized"
- "install"
- "env"
- "port"
- "docker"

### coding
Use for:
- writing code
- refactoring
- debugging source files
- tests
- APIs
- scripts
- schema design
- workflow logic
- plugin or tool development

Signals:
- "write a script"
- "refactor"
- "debug code"
- "function"
- "class"
- "json schema"
- "sql"
- "n8n workflow"

### rag
Use for:
- indexing
- embeddings
- vector storage
- retrieval pipelines
- hybrid search
- document parsing
- metadata enrichment
- chunking
- semantic memory
- library management

Signals:
- "RAG"
- "embedding"
- "vector"
- "index"
- "retrieve"
- "semantic search"
- "metadata"
- "document ingestion"

### browser
Use for:
- websites
- scraping
- page inspection
- form interaction
- login flow analysis
- UI troubleshooting
- publishing tasks

Signals:
- "website"
- "page"
- "browser"
- "playwright"
- "click"
- "form"
- "wordpress"
- "post to website"

### vision_qc
Use for:
- checking image consistency
- comparing generated images
- caption placement review
- visual defect detection
- scene continuity
- character consistency
- composition review

Signals:
- "compare these images"
- "consistent character"
- "quality control"
- "image drift"
- "same clothes"
- "same face"
- "visual review"

### creative_prompting
Use for:
- image prompts
- video prompts
- scene prompts
- style prompts
- shot prompts
- rewrite prompt for better generation
- storytelling prompt engineering

Signals:
- "prompt"
- "scene"
- "cinematic"
- "style"
- "generate image"
- "consistent character prompt"

### planning
Use for:
- architecture
- system design
- rollout plans
- phased implementation
- product structure
- repo organization
- naming and capability mapping

Signals:
- "plan"
- "architecture"
- "step by step"
- "roadmap"
- "design"
- "how should I structure"

### file_ops
Use for:
- file moves
- rename rules
- sync layout
- storage balancing
- archive strategy
- library organization
- provider placement logic

Signals:
- "move files"
- "organize"
- "rename"
- "sync"
- "archive"
- "storage"
- "S3"
- "Google Drive"
- "Dropbox"
- "NAS"

### troubleshooting
Use when the task spans multiple classes but the main goal is diagnosis and recovery.
This is the fallback class when the request is primarily about determining cause.

## Agent role mapping

Map the request to one role:

### brodie
Use for:
- infrastructure
- orchestration
- shell
- system operations
- repo management
- agent coordination
- storage policy
- automation control

### arty
Use for:
- media prompts
- visual generation workflows
- scene descriptions
- creative asset production
- caption aesthetics
- multimedia transformations

### coding
Use for:
- implementation-heavy code work
- schema work
- scripts
- APIs
- debugging

### rag
Use for:
- retrieval architecture
- embeddings
- indexing
- document understanding
- search relevance

### vision
Use for:
- image review
- scene comparison
- consistency analysis
- visual QA

If uncertain:
- prefer brodie for operations
- prefer coding for implementation
- prefer rag for retrieval
- prefer arty for generative media
- prefer vision for image comparison

## Mode mapping

Select exactly one mode:

### strict
Use for:
- shell
- production config
- migrations
- destructive actions
- security-sensitive work
- diagnosis where precision matters most

Behavior:
- minimal creativity
- explicit assumptions
- verify before change
- prefer deterministic steps
- keep outputs constrained

### safe
Use for:
- troubleshooting
- browser tasks with risk
- file operations
- infrastructure planning that may affect live systems

Behavior:
- conservative
- validate inputs
- avoid speculative edits
- propose rollback-aware actions

### balanced
Use for:
- general coding
- RAG design
- planning
- mixed operational tasks

Behavior:
- practical
- adaptive
- moderate exploration
- concise but complete

### creative
Use for:
- arty tasks
- prompt design
- visual concept generation
- variant ideation
- media direction

Behavior:
- broad exploration
- more diverse candidate outputs
- still remain on task

## Default mapping matrix

Use this matrix unless the user explicitly wants a different style:

- shell -> role brodie -> mode strict
- coding -> role coding -> mode balanced
- rag -> role rag -> mode balanced
- browser -> role brodie -> mode safe
- vision_qc -> role vision -> mode balanced
- creative_prompting -> role arty -> mode creative
- planning -> role brodie -> mode balanced
- file_ops -> role brodie -> mode safe
- troubleshooting -> role brodie -> mode safe

## Execution rules by class

### For shell
- prefer deterministic commands
- inspect before editing
- read logs before proposing cause
- do not guess paths if they can be discovered
- state the likely fault chain clearly
- if editing service config, preserve rollback path

Recommended preset style:
- low randomness
- concise output
- stronger repetition control
- bounded output length

### For coding
- produce usable code
- prefer correctness over novelty
- include comments only where they help maintenance
- preserve user conventions if known
- avoid unnecessary abstractions

Recommended preset style:
- moderate randomness
- medium output length
- keep formatting predictable

### For rag
- optimize for accuracy, recall, and traceability
- separate ingestion, indexing, retrieval, and ranking concerns
- maintain metadata fidelity
- keep document identity stable

Recommended preset style:
- low to moderate randomness
- medium output length
- structured reasoning

### For browser
- prefer official pages and direct evidence
- distinguish page observation from inference
- be careful with auth or posting flows
- do not claim actions succeeded unless confirmed

Recommended preset style:
- low randomness
- medium output length
- careful extraction

### For vision_qc
- compare identity, clothing, pose, background, framing, lighting, and artifacts
- identify drift precisely
- suggest targeted prompt changes, not vague rewrites
- separate observed mismatch from recommended correction

Recommended preset style:
- low to moderate randomness
- concise analytical output

### For creative_prompting
- generate strong, reusable prompts
- preserve anchor traits across variants
- keep style instructions and subject identity distinct
- for consistency, lock immutable features first

Recommended preset style:
- higher randomness
- broader variant range
- medium to high output length when needed

### For planning
- structure in phases
- identify dependencies
- prefer practical sequencing
- keep names and boundaries stable

Recommended preset style:
- moderate randomness
- medium output length
- structured output

### For file_ops
- preserve traceability of file location
- prefer stable IDs over path-only identity
- consider storage cost, limits, redundancy, and searchability
- propose human-readable folder layout

Recommended preset style:
- low randomness
- structured output
- conservative actions

### For troubleshooting
- identify symptom
- identify probable cause
- identify highest-value checks
- propose smallest safe fix first
- then verify

Recommended preset style:
- low randomness
- concise analysis
- bounded length

## Provider-aware guidance

Use this only when generating preset JSON or discussing config:

### OpenAI-compatible
Prefer fields such as:
- temperature
- top_p
- max_tokens or max_completion_tokens
- stop

### Ollama
Common fields may include:
- temperature
- top_p
- top_k
- repeat_penalty
- num_predict
- stop

### Anthropic
Common controls may include:
- temperature
- top_p
- max_tokens
- stop_sequences

### Gemini
Common controls may include:
- temperature
- topP
- topK
- maxOutputTokens
- stopSequences

Do not invent unsupported provider fields.
If uncertain, emit conceptual guidance first and config JSON second.

## Output contract for this skill

When this skill is used, produce this structure in plain text:

Task class: <one value>
Role: <one value>
Mode: <one value>

Reason:
<brief explanation>

Execution style:
<brief operational guidance>

Optional preset guidance:
<only include if useful>

If the user asks for machine-readable config, then also provide:
- a JSON block
- provider-specific field names
- a short note on where it should be placed

## Helper script rule

If this skill folder contains a helper script for preset generation:
- use it only when the user asks for preset JSON or config output
- do not run it for simple advisory requests
- validate that the provider and role names match this skill's classification

## Safety and restraint

- Do not pretend the preset was applied automatically unless a real config change was made.
- Do not claim a command succeeded without evidence.
- Do not classify the request into multiple primary classes unless the user explicitly asks for a multi-pass plan.
- If uncertain between two classes, choose the one that reduces operational risk.

## Examples

User request:
"Check why the OpenClaw gateway LaunchAgent is failing after reboot."

Return:
Task class: shell
Role: brodie
Mode: strict

Reason:
The task is operational, service-oriented, and requires deterministic diagnosis.

Execution style:
Inspect plist, logs, env, token config, and launchctl state before making edits.

User request:
"Write me a better image prompt to keep the same actress and clothing across five scenes."

Return:
Task class: creative_prompting
Role: arty
Mode: creative

Reason:
The primary task is prompt engineering for visual generation consistency.

Execution style:
Lock subject anchors first, then environment and shot variation, then negative constraints.

User request:
"Help me redesign my document indexing and vector storage flow."

Return:
Task class: rag
Role: rag
Mode: balanced

Reason:
The task is retrieval architecture and indexing design.

Execution style:
Separate ingestion, chunking, embedding, metadata, retrieval, and reranking into distinct stages.
