import json
import sys

TASK_MAP = {
 "shell": ("operator","operational"),
 "browser": ("operator","operational"),
 "rag": ("researcher","analytical"),
 "troubleshooting": ("debugger","analytical"),
 "file_ops": ("operator","operational"),
 "creative": ("creator","creative"),
 "planning": ("planner","analytical")
}

MODE_PRESETS = {
 "operational": {"temperature":0.2,"top_p":0.9,"max_tokens":1200},
 "analytical": {"temperature":0.4,"top_p":0.9,"max_tokens":1600},
 "creative": {"temperature":0.8,"top_p":0.95,"max_tokens":2000}
}

task = sys.argv[1] if len(sys.argv) > 1 else "planning"

role,mode = TASK_MAP.get(task,("planner","analytical"))
preset = MODE_PRESETS[mode]

output = {
 "role": role,
 "mode": mode,
 **preset
}

print(json.dumps(output,indent=2))
