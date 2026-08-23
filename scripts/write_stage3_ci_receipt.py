#!/usr/bin/env python3
import json
import os
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "benchmark/results/STAGE3_CI_LATEST.json"

STEP_KEYS = [
    "validate_semantics",
    "validate_plans",
    "probe_v2",
    "assets",
    "variant_inputs",
    "build_native",
    "audit_native",
    "build_hybrid",
    "audit_hybrid",
    "panic_native",
    "panic_hybrid",
]


def maybe_json(path):
    path = ROOT / path
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"read_error": str(exc), "path": str(path.relative_to(ROOT))}


def main():
    steps = {key: os.getenv(f"STAGE3_{key.upper()}", "unknown") for key in STEP_KEYS}
    receipt = {
        "schema_version": "stage3-ci-receipt-v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "workflow_status": os.getenv("STAGE3_JOB_STATUS", "unknown"),
        "commit": os.getenv("GITHUB_SHA"),
        "run_id": os.getenv("GITHUB_RUN_ID"),
        "run_attempt": os.getenv("GITHUB_RUN_ATTEMPT"),
        "steps": steps,
        "artifacts_present": {
            "native_vector_pptx": (ROOT / "dist/queuezero_native_vector.pptx").exists(),
            "hybrid_pptx": (ROOT / "dist/queuezero_hybrid.pptx").exists(),
            "ppt_master_trace": (ROOT / "dist/ppt_master_adapter_workspace/trace.json").exists(),
        },
        "panic": {
            "native_vector": maybe_json("dist/panic/native_vector/summary.json"),
            "hybrid": maybe_json("dist/panic/hybrid/summary.json"),
        },
        "notes": [
            "Hybrid Problem hero remains a deterministic structural fixture and must not be used for blind visual-quality scoring.",
            "A failed workflow receipt identifies the first failed stage via step outcomes; detailed logs remain in GitHub Actions."
        ],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(OUT.relative_to(ROOT))


if __name__ == "__main__":
    main()
