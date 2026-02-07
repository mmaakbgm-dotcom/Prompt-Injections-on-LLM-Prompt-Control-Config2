import os

os.environ.pop("AI_INTEGRATIONS_OPENAI_API_KEY", None)
os.environ.pop("AI_INTEGRATIONS_OPENAI_BASE_URL", None)

import asyncio
import json
import time
from pathlib import Path
from typing import Any

from deepteam import red_team
from deepteam.vulnerabilities import (
    IndirectInstruction,
    ToolMetadataPoisoning,
    ToolOrchestrationAbuse,
    RecursiveHijacking,
    GoalTheft,
    PromptLeakage,
)

from clinic import authenticate, is_authenticated, customer_chat


# DeepTeam is running in async mode; callback MUST be async.
async def model_callback(user_input: str) -> str:
    def _run_blocking() -> str:
        # keep session stable; only auth once
        if not is_authenticated():
            authenticate("alice", "alice123")  # change if needed
        return str(customer_chat(user_input))

    return await asyncio.to_thread(_run_blocking)


def _json_safe(obj: Any):
    """
    DeepTeam puts enums / custom objects into the report; make them JSON-safe.
    """
    if hasattr(obj, "value"):
        try:
            return obj.value
        except Exception:
            pass
    if hasattr(obj, "name"):
        try:
            return obj.name
        except Exception:
            pass
    return str(obj)


def main():
    out_dir = Path("deepteam_runs")
    out_dir.mkdir(exist_ok=True)

    ts = time.strftime("%Y%m%d-%H%M%S")
    txt_path = out_dir / f"deepteam_{ts}.txt"
    json_path = out_dir / f"deepteam_{ts}.json"

    # “Strongest prompt-injection combo” (high-signal set)
    # - IndirectInstruction: RAG/tool-output/cross-context injection
    # - ToolMetadataPoisoning: schema/description deception
    # - ToolOrchestrationAbuse: unsafe tool composition/state leakage/budget abuse
    # - RecursiveHijacking + GoalTheft: goal drift / probing / social-engineering
    # - PromptLeakage: leakage → better injections chain
    vulns = [
        IndirectInstruction(),
        ToolMetadataPoisoning(),
        ToolOrchestrationAbuse(),
        RecursiveHijacking(),
        GoalTheft(),
        PromptLeakage(),
    ]

    # IMPORTANT: do NOT "await" this. red_team returns an object, not a coroutine.
    report = red_team(
        model_callback=model_callback,
        vulnerabilities=vulns,
    )

    txt = str(report)
    txt_path.write_text(txt, encoding="utf-8")

    payload = {"raw_str": txt}

    structured = None
    for attr in ("model_dump", "dict", "to_dict"):
        fn = getattr(report, attr, None)
        if callable(fn):
            try:
                structured = fn()
                break
            except Exception:
                structured = None

    if structured is not None:
        payload["structured"] = structured

    json_path.write_text(
        json.dumps(payload, indent=2, default=_json_safe),
        encoding="utf-8",
    )

    print("\n✅ DeepTeam run complete")
    print(f"- {txt_path}")
    print(f"- {json_path}\n")
    print(report)


if __name__ == "__main__":
    main()