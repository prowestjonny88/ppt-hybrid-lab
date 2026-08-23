import hashlib
import json
import re
from pathlib import Path

_BINDING_RE = re.compile(r"\{([A-Za-z0-9_-]+)\.display_value\}")


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def canonical_hash(data):
    raw = json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def evidence_index(semantics):
    return {item["evidence_id"]: item for item in semantics.get("evidence", [])}


def object_index(semantics):
    return {item["object_id"]: item for item in semantics.get("semantic_objects", [])}


def region_index(semantics):
    return {item["region_id"]: item for item in semantics.get("regions", [])}


def asset_index(semantics):
    return {item["asset_id"]: item for item in semantics.get("assets", [])}


def resolve_template(value, semantics):
    if value is None or not isinstance(value, str):
        return value
    evidence = evidence_index(semantics)

    def repl(match):
        evidence_id = match.group(1)
        if evidence_id not in evidence:
            raise KeyError(f"unknown evidence binding {evidence_id!r}")
        display = evidence[evidence_id].get("display_value")
        return "" if display is None else str(display)

    return _BINDING_RE.sub(repl, value)


def resolved_object_text(obj, semantics):
    if "content_ref" in obj:
        evidence = evidence_index(semantics)[obj["content_ref"]]
        return "" if evidence.get("display_value") is None else str(evidence["display_value"])
    if "content_template" in obj:
        return resolve_template(obj["content_template"], semantics)
    return resolve_template(obj.get("content", ""), semantics)


def semantic_file_hash(path):
    return canonical_hash(load_json(path))
