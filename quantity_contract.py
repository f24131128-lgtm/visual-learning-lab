"""Small numeric provenance contract shared by declarations and value owners.

Source assertions stay in immutable specifications. Learner state contains only
exploration values. Names, labels and subject matter never grant write access.
"""
import math
import re
import ast

VERSION = "1.0"
ROLES = ("source_fixed", "source_variable", "hypothetical_exploration", "derived")
ROLE_SCHEMA = {"type": "string", "enum": list(ROLES)}
REF_SCHEMA = {"type": ["string", "null"]}
PAGES_SCHEMA = {"type": "array", "items": {"type": "integer", "minimum": 1}, "maxItems": 8}
PROVENANCE_FIELDS = dict(provenance=ROLE_SCHEMA, source_baseline_ref=REF_SCHEMA,
                         source_evidence={"type": "string", "maxLength": 240},
                         expose_control={"type": "boolean"})


def object_schema(fields):
    return dict(type="object", properties=fields, required=list(fields), additionalProperties=False)


FACT_SCHEMA = object_schema(dict(id={"type": "string"}, label={"type": "string"},
    unit={"type": "string"}, value={"type": "number", "minimum": -1e9, "maximum": 1e9},
    provenance={"type": "string", "enum": ["source_fixed"]}, source_pages=PAGES_SCHEMA,
    source_evidence={"type": "string", "maxLength": 240}))
FACTS_SCHEMA = dict(type="array", items=FACT_SCHEMA, maxItems=12)


def finite(value):
    if type(value) not in (int, float) or not math.isfinite(value) or abs(value) > 1e9:
        raise ValueError("Invalid quantity value")
    return float(value)


def evidence(item, allowed_pages):
    pages = item.get("source_pages")
    if (not isinstance(pages, list) or len(pages) > 8 or len(set(pages)) != len(pages)
            or any(type(p) is not int or p not in allowed_pages for p in pages)):
        raise ValueError("Invalid quantity source pages")
    text = item.get("source_evidence")
    if (not isinstance(text, str) or len(text) > 240 or not text.strip()
            or re.search(r"[<>\x00-\x1f]", text)):
        raise ValueError("Missing quantity source evidence")
    # Pasted text has no invented page numbers; its bounded evidence is retained.
    if allowed_pages and not pages:
        raise ValueError("Missing quantity source page")


def normalize_facts(raw, allowed_pages, reserved=()):
    if not isinstance(raw, list) or len(raw) > 12:
        raise ValueError("Invalid source fact count")
    result, seen = [], set(reserved)
    for item in raw:
        if not isinstance(item, dict) or set(item) != set(FACT_SCHEMA["properties"]):
            raise ValueError("Invalid source fact fields")
        identifier = item["id"]
        if (not isinstance(identifier, str) or not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]{0,47}", identifier)
                or "__" in identifier or identifier in seen or identifier in ("time", "pi", "e", "sin", "cos", "tan", "exp", "log", "sqrt", "abs")):
            raise ValueError("Invalid source fact identity")
        seen.add(identifier)
        if item["provenance"] != "source_fixed":
            raise ValueError("Source fact must be immutable")
        evidence(item, allowed_pages)
        for key in ("label", "unit"):
            if not isinstance(item[key], str) or len(item[key]) > 100 or re.search(r"[<>\x00-\x1f]", item[key]):
                raise ValueError("Invalid source fact text")
        result.append(dict(item, value=finite(item["value"]), source_pages=list(item["source_pages"])))
    return result


def validate_parameter(p, facts, allowed_pages):
    if p.get("provenance") not in ROLES or type(p.get("expose_control")) is not bool:
        raise ValueError("Missing quantity provenance/control policy")
    role = p["provenance"]
    if role == "derived":
        raise ValueError("Derived quantity cannot be a parameter")
    if role in ("source_fixed", "source_variable"):
        evidence(p, allowed_pages)
    elif (not isinstance(p.get("source_evidence"), str) or len(p["source_evidence"]) > 240
          or re.search(r"[<>\x00-\x1f]", p["source_evidence"])):
        raise ValueError("Invalid exploration evidence")
    ref = p.get("source_baseline_ref")
    if ref is not None and (role != "hypothetical_exploration" or ref not in facts or ref == p["id"]):
        raise ValueError("Invalid or shared source baseline identity")
    if role == "source_fixed" and (p["min"] != p["max"] or p["default"] != p["min"] or p["step"] != 0 or p["expose_control"]):
        raise ValueError("Source fixed quantity cannot be adjustable")


def can_commit(p):
    return (p.get("provenance") in ("source_variable", "hypothetical_exploration")
            and p.get("expose_control") is True and p["min"] < p["max"])


def check_commit(p, value):
    value = finite(value)
    if not can_commit(p) or not p["min"] <= value <= p["max"]:
        raise ValueError("Quantity does not permit this learner commit")
    return value


def check_values(parameters, values):
    if set(values) != {p["id"] for p in parameters}:
        raise ValueError("Invalid canonical quantity state")
    for p in parameters:
        value = finite(values[p["id"]])
        if not p["min"] <= value <= p["max"]:
            raise ValueError("Quantity outside numeric domain")
        if not can_commit(p) and value != p["default"]:
            raise ValueError("Read-only quantity changed")


def source_values(spec):
    return ({f["id"]: f["value"] for f in spec.get("source_facts", [])}
            | {p["id"]: p["default"] for p in spec.get("parameters", []) if p.get("provenance") == "source_fixed"})


def expression_names(expression, allowed):
    """Keep the existing per-expression limit; unused facts consume no operands."""
    from safe_math import CONSTANTS, FUNCTIONS, MAX_EXPRESSION_LENGTH, MathExpressionError
    if not isinstance(expression, str) or not 1 <= len(expression) <= MAX_EXPRESSION_LENGTH:
        raise MathExpressionError("Invalid quantity expression length")
    try: tree = ast.parse(expression, mode="eval")
    except (SyntaxError, RecursionError) as error: raise MathExpressionError("Invalid quantity expression") from error
    names = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)} - CONSTANTS.keys() - FUNCTIONS.keys()
    if not names <= set(allowed): raise MathExpressionError("Unknown declared quantity")
    return names


def validate_quantity_expression(expression, allowed):
    from safe_math import validate_expression
    return validate_expression(expression, expression_names(expression, allowed))


def evaluate_quantity(expression, values):
    from safe_math import evaluate_expression
    return evaluate_expression(expression, {k: values[k] for k in expression_names(expression, values)})
