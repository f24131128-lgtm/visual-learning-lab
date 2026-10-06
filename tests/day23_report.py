"""Regenerate review tables from immutable recordings; no network/model calls."""
import json
from pathlib import Path
import day23_benchmark as bench
from day23_review import review


def main():
    manifest = bench.read_manifest()
    home = bench.HOME
    before = json.loads((home / "phase_a-audit/results.json").read_text(encoding="utf-8"))
    after = json.loads((home / "phase_b-audit/results.json").read_text(encoding="utf-8"))
    semantic = review()
    bench.save(home / "semantic_review.json", semantic)
    rows = []
    for a, b in zip(before["rows"], after["rows"], strict=True):
        assert a["material_id"] == b["material_id"]
        failure = "R3" if b["material_id"] == "recursive_calls" else b["failure_category"]
        rows.append(dict(material_id=b["material_id"], before=a, after=b, reviewed_failure=failure))
    output = dict(corpus_sha256=manifest["corpus_sha256"], before=before["summary"],
        after=after["summary"], semantic_review=semantic, rows=rows)
    bench.save(home / "comparison.json", output)
    table = ["# Same frozen corpus comparison", "", "Gold: agent-authored before execution; independent human approval pending.", "",
        "| Case | A proposal / selected | A artifact / local | B selected | B artifact / local | Semantic review |",
        "|---|---|---|---|---|---|"]
    for r in rows:
        a, b = r["before"], r["after"]
        table.append(f"| {r['material_id']} | {a['proposal_family']} / {a['selected_family']} | {a['compilation_pass']} / {a['runtime_pass']} | {b['selected_family']} | {b['compilation_pass']} / {b['runtime_pass']} | {r['reviewed_failure'] or 'source equation/operation or honest static checked'} |")
    (home / "comparison.md").write_text("\n".join(table) + "\n", encoding="utf-8")
    packet = ["# Frozen gold review packet", "", "The following judgments were frozen before execution. Human approval remains pending. Do not rewrite the manifest to match results.", ""]
    for case in manifest["payload"]["materials"]:
        packet += [f"## {case['material_id']}", "", f"Material: [original text](materials/{case['material_id']}.txt)", "",
            f"Traits: {', '.join(case['semantic_traits'])}.", "",
            f"Primary: **{case['primary_family']}**; acceptable set: {', '.join(case['acceptable_families'])}.", "",
            case["gold_reason"], "", f"Expected interaction: {case['expected_interaction']}", "",
            "Human decision: pending. Any correction must be dated, explained, and scored separately.", ""]
    (home / "GOLD_REVIEW_PACKET.md").write_text("\n".join(packet), encoding="utf-8")
    print(json.dumps(dict(corpus_sha256=manifest["corpus_sha256"], meaningful=semantic["meaningful_runtime_pass"], cases=len(rows))))


if __name__ == "__main__":
    main()
