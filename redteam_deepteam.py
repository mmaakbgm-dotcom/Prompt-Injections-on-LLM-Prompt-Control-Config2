    import asyncio
    import json
    import os
    import time
    from pathlib import Path
    from typing import Any

    from deepteam import red_team
    from deepteam.vulnerabilities import (
        PromptLeakage,
        IndirectInstruction,
        ToolMetadataPoisoning,
        ToolOrchestrationAbuse,
        RecursiveHijacking,
        GoalTheft,
        ExcessiveAgency,
    )

    from deepeval.models import GPTModel

    from clinic import authenticate, is_authenticated, customer_chat


    # -----------------------------
    # App callback (YOUR system)
    # -----------------------------
    async def model_callback(user_input: str) -> str:
        def _run():
            if not is_authenticated():
                authenticate("alice", "alice123")
            return str(customer_chat(user_input))

        return await asyncio.to_thread(_run)


    # -----------------------------
    # JSON safety helper
    # -----------------------------
    def _json_safe(obj: Any):
        if hasattr(obj, "value"):
            return obj.value
        if hasattr(obj, "name"):
            return obj.name
        return str(obj)


    # -----------------------------
    # Main runner
    # -----------------------------
    def main():
        # 🔴 HARD FAIL if key missing
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key or not api_key.startswith("sk-"):
            raise RuntimeError("OPENAI_API_KEY not set or invalid")

        out_dir = Path("deepteam_runs")
        out_dir.mkdir(exist_ok=True)

        ts = time.strftime("%Y%m%d-%H%M%S")
        txt_path = out_dir / f"deepteam_{ts}.txt"
        json_path = out_dir / f"deepteam_{ts}.json"

        # 🔥 STRONGEST PROMPT-INJECTION COMBO
        vulnerabilities = [
            PromptLeakage(),
            IndirectInstruction(),
            ToolMetadataPoisoning(),
            ToolOrchestrationAbuse(),
            RecursiveHijacking(),
            GoalTheft(),
            ExcessiveAgency(),
        ]

        # 🔥 THIS IS THE CRITICAL FIX
        simulator = GPTModel(
            model="gpt-4o-mini",
            api_key=api_key,
        )

        report = red_team(
            model_callback=model_callback,
            vulnerabilities=vulnerabilities,
            simulator_model=simulator,
        )

        # Save text
        txt = str(report)
        txt_path.write_text(txt, encoding="utf-8")

        # Save JSON
        payload = {"raw": txt}
        for fn_name in ("model_dump", "dict", "to_dict"):
            fn = getattr(report, fn_name, None)
            if callable(fn):
                try:
                    payload["structured"] = fn()
                    break
                except Exception:
                    pass

        json_path.write_text(
            json.dumps(payload, indent=2, default=_json_safe),
            encoding="utf-8",
        )

        print("\n✅ DeepTeam run complete")
        print(f"- {txt_path}")
        print(f"- {json_path}")
        print(report)


    if __name__ == "__main__":
        main()