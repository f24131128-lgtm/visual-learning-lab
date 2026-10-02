"""Explicit live compiler probe. Never imported/run by automated tests or app.

Run from the repository root: python -B -m tests.probe_day18_compiler --live
Uses only the public acceptance text; no PDF, raw user source or secrets logged.
"""

import argparse
import ast
import json
from pathlib import Path
import tomllib

from openai import OpenAI
from scene.compiler import build_scene_context, request_scene
from scene.validator import normalize_scene
from .day18_acceptance import THREE_PHASE_TEXT, acceptance_analysis


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true", help="Make one real Responses request using configured credentials.")
    args = parser.parse_args()
    if not args.live:
        parser.error("--live is required; this command spends one compiler request.")
    # Read the application model without executing the Streamlit entry point.
    root = Path(__file__).resolve().parents[1]
    tree = ast.parse((root/"app.py").read_text(encoding="utf-8"))
    model = next(n.value.value for n in tree.body if isinstance(n, ast.Assign)
                 and any(isinstance(t, ast.Name) and t.id == "MODEL" for t in n.targets))
    config = tomllib.loads((root/".streamlit/secrets.toml").read_text(encoding="utf-8"))
    client = OpenAI(api_key=config["OPENAI_API_KEY"], timeout=120, max_retries=0)
    context = build_scene_context(acceptance_analysis(), dict(kind="text", source_text=THREE_PHASE_TEXT), [], "spatial_dynamics")
    raw = request_scene(client, model, context)
    result = dict(model=model, compiler_received=True, raw=raw)
    try:
        scene = normalize_scene(raw, [])
        result.update(accepted=True, validation=scene["validation_report"])
    except ValueError as error:
        result.update(accepted=False, validator_reason=str(error))
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
