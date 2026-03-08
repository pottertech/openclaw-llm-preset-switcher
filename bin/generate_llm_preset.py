#!/usr/bin/env python3
import argparse
import json
import sys

TASK_MAP = {
    "shell": {"role": "brodie", "mode": "strict"},
    "coding": {"role": "coding", "mode": "balanced"},
    "rag": {"role": "rag", "mode": "balanced"},
    "browser": {"role": "brodie", "mode": "safe"},
    "vision_qc": {"role": "vision", "mode": "balanced"},
    "creative_prompting": {"role": "arty", "mode": "creative"},
    "planning": {"role": "brodie", "mode": "balanced"},
    "file_ops": {"role": "brodie", "mode": "safe"},
    "troubleshooting": {"role": "brodie", "mode": "safe"},
}

MODE_PRESETS = {
    "strict": {
        "temperature": 0.15,
        "top_p": 0.85,
        "top_k": 30,
        "max_tokens": 900,
        "repeat_penalty": 1.12,
        "stop": []
    },
    "safe": {
        "temperature": 0.3,
        "top_p": 0.9,
        "top_k": 40,
        "max_tokens": 1200,
        "repeat_penalty": 1.08,
        "stop": []
    },
    "balanced": {
        "temperature": 0.5,
        "top_p": 0.92,
        "top_k": 50,
        "max_tokens": 1600,
        "repeat_penalty": 1.05,
        "stop": []
    },
    "creative": {
        "temperature": 0.85,
        "top_p": 0.97,
        "top_k": 80,
        "max_tokens": 2000,
        "repeat_penalty": 1.02,
        "stop": []
    },
}

PROVIDER_FIELDS = {
    "openai": {
        "temperature": "temperature",
        "top_p": "top_p",
        "max_tokens": "max_tokens",
        "stop": "stop",
    },
    "ollama": {
        "temperature": "temperature",
        "top_p": "top_p",
        "top_k": "top_k",
        "repeat_penalty": "repeat_penalty",
        "max_tokens": "num_predict",
        "stop": "stop",
    },
    "anthropic": {
        "temperature": "temperature",
        "top_p": "top_p",
        "max_tokens": "max_tokens",
        "stop": "stop_sequences",
    },
    "gemini": {
        "temperature": "temperature",
        "top_p": "topP",
        "top_k": "topK",
        "max_tokens": "maxOutputTokens",
        "stop": "stopSequences",
    },
}


def render(provider: str, task_class: str, mode_override: str | None, tokens: int | None):
    mapping = TASK_MAP[task_class]
    role = mapping["role"]
    mode = mode_override or mapping["mode"]
    preset = dict(MODE_PRESETS[mode])
    if tokens is not None:
        preset["max_tokens"] = tokens

    fields = PROVIDER_FIELDS[provider]
    out = {
        "task_class": task_class,
        "role": role,
        "mode": mode,
        "provider": provider,
        "preset": {},
    }

    for key, value in preset.items():
        if key in fields:
            out["preset"][fields[key]] = value

    return out


def main():
    parser = argparse.ArgumentParser(description="Generate provider-aware preset JSON for the OpenClaw llm preset switcher skill.")
    parser.add_argument("--provider", required=True, choices=sorted(PROVIDER_FIELDS.keys()))
    parser.add_argument("--task-class", required=True, choices=sorted(TASK_MAP.keys()))
    parser.add_argument("--mode", choices=sorted(MODE_PRESETS.keys()))
    parser.add_argument("--tokens", type=int)
    args = parser.parse_args()

    result = render(args.provider, args.task_class, args.mode, args.tokens)
    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
