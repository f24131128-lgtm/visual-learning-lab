"""Explicit offline packaging of the owner-approved Day26 archive derivative.

Never calls a provider. Does not copy session state, credentials, or diagnostics.
Run with --archive .day26-local/open-twin.json --pdf ORIGINAL.pdf.
The historical declarations remain unchanged; only the derivative gains v2.4
provenance declarations. See prepared/projectile/PROVENANCE.md.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
PDF_SHA = "688a232388f914ed834e02b28ba343c10b3866e23c3cd94ff38f859957d0c5ec"
ARCHIVE_SHA = "2501e0e915172fea100312aa9409c798257683f48842635fa361108ba528363b"


def project_fields(value, schema):
    if isinstance(value, dict) and "properties" in schema:
        return {k: project_fields(value[k], child) for k, child in schema["properties"].items()}
    if isinstance(value, list) and "items" in schema:
        return [project_fields(item, schema["items"]) for item in value]
    return copy.deepcopy(value)


def derive(archived):
    from scene.world.schema import WORLD_SCHEMA, VERSION
    scene = copy.deepcopy(archived)
    if scene.get("scene_version") != "2.2" or scene.get("scene_id") != "ideal_projectile_motion":
        raise ValueError("Not the reviewed Day26 archive")
    scene.update(scene_version=VERSION, source_facts=[])
    for p in scene["parameters"]:
        # Neither the 20 m/s, 45-degree, 2 m defaults nor g=9.8 are
        # asserted to be Figure 5.3 example values. g remains read-only.
        p.update(provenance="hypothetical_exploration", source_baseline_ref=None,
                 source_evidence="Day26 compiled exploration assumption; not a numeric assertion from Figure 5.3.",
                 expose_control=p["min"] < p["max"],
                 domain_constraint="positive" if p["quantity_kind"] in ("speed", "acceleration", "inclination_angle") else "non_negative")
        p["range_source"] = "pedagogical"
    for q in scene["quantities"]:
        q["provenance"] = "derived"
    return project_fields(scene, WORLD_SCHEMA)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--pdf", type=Path, required=True)
    args = parser.parse_args()
    pdf = args.pdf.read_bytes()
    if hashlib.sha256(pdf).hexdigest() != PDF_SHA:
        raise ValueError("Original Day26 PDF hash mismatch")
    archive_bytes = args.archive.read_bytes()
    if hashlib.sha256(archive_bytes).hexdigest() != ARCHIVE_SHA:
        raise ValueError("Reviewed Day26 archive hash mismatch")
    archive = json.loads(archive_bytes)
    from source_atlas.schema import ATLAS_SCHEMA
    from scene.validator import normalize_scene
    scene = derive(archive["scene"])
    normalize_scene(scene, archive["allowed_pages"])
    target = ROOT / "prepared/projectile"
    target.mkdir(exist_ok=True)
    content = {"source.pdf": pdf, "analysis.json": archive["analysis"],
               "scene.json": scene, "atlas.json": project_fields(archive["atlas"], ATLAS_SCHEMA),
               "archived_scene.json": archive["scene"]}
    for name, data in content.items():
        (target/name).write_bytes(data if isinstance(data, bytes) else
            (json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False)+"\n").encode("utf-8"))
    manifest = dict(version="1.0", source="MIT OpenCourseWare / Peter Dourmashkin, Chapter 5: Two Dimensional Kinematics",
        url="https://ocw.mit.edu/courses/8-01sc-classical-mechanics-fall-2016/resources/mit8_01scs22_chapter5/",
        license="CC BY-NC-SA 4.0", prepared=True, provenance="Owner-approved Day26 archive derivative, revalidated under World 2.4; not an unmodified historical AI response.",
        archive_sha256=hashlib.sha256(archive_bytes).hexdigest(),
        historical_material=archive["material"], source_pdf_bytes=len(pdf), source_pdf_pages=16,
        initial_page=4, initial_region="p4_velocity_decomposition_diagram",
        sha256={name: hashlib.sha256((target/name).read_bytes()).hexdigest() for name in content})
    (target/"manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print("Packaged reviewed derivative; original PDF SHA-256 verified. No provider request.")


if __name__ == "__main__":
    main()
