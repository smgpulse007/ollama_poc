"""Offline exact-field regression checks for structured document extraction.

Uses only the Python standard library. Reports paths and counts, never values.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON object key")
        result[key] = value
    return result


def _reject_constant(value):
    raise ValueError("non-finite numbers are not valid JSON")


def parse_json(text: str) -> Any:
    def finite_float(value):
        parsed = float(value)
        if not math.isfinite(parsed):
            raise ValueError("non-finite numbers are not valid JSON")
        return parsed

    return json.loads(text, object_pairs_hook=_unique_object,
                      parse_constant=_reject_constant, parse_float=finite_float)


def read_records(path: Path) -> dict[str, dict]:
    records = {}
    with path.open(encoding="utf-8-sig") as stream:
        for line_number, line in enumerate(stream, 1):
            if not line.strip():
                continue
            try:
                record = parse_json(line)
            except ValueError as exc:
                raise ValueError(f"invalid JSONL at line {line_number}") from exc
            if not isinstance(record, dict) or not isinstance(record.get("id"), str) or not record["id"]:
                raise ValueError(f"line {line_number} requires a nonempty string id")
            if record["id"] in records:
                raise ValueError(f"duplicate record id at line {line_number}")
            records[record["id"]] = record
    return records


def _leaves(value: Any, path: str = "") -> dict[str, Any]:
    if isinstance(value, dict) and value:
        result = {}
        for key, child in value.items():
            token = key.replace("~", "~0").replace("/", "~1")
            result.update(_leaves(child, path + "/" + token))
        return result
    if isinstance(value, list) and value:
        result = {}
        for index, child in enumerate(value):
            result.update(_leaves(child, path + "/" + str(index)))
        return result
    return {path: value}


def _equal(expected: Any, actual: Any) -> bool:
    # JSON numbers may be represented as int or float; booleans are not numbers.
    if type(expected) in (int, float) and type(actual) in (int, float):
        return expected == actual
    return type(expected) is type(actual) and expected == actual


def _containers(value: Any, path: str = "") -> dict[str, type]:
    result = {}
    if isinstance(value, (dict, list)):
        result[path] = type(value)
        items = value.items() if isinstance(value, dict) else enumerate(value)
        for key, child in items:
            token = str(key).replace("~", "~0").replace("/", "~1")
            result.update(_containers(child, path + "/" + token))
    return result


def evaluate(cases: dict[str, dict], predictions: dict[str, dict]) -> dict:
    if not cases:
        raise ValueError("at least one reference case is required")
    if predictions.keys() - cases.keys():
        raise ValueError("predictions contain unknown case ids")
    results = []
    for case_id, case in cases.items():
        if not isinstance(case.get("expected"), dict):
            raise ValueError("every reference case requires an expected object")
        expected = _leaves(case["expected"])
        status = "ok"
        actual = {}
        wrong_containers = set()
        if case_id not in predictions:
            status = "missing_prediction"
        else:
            try:
                output = predictions[case_id]["output"]
                output = parse_json(output) if isinstance(output, str) else output
                if not isinstance(output, dict):
                    raise ValueError("output must be an object")
                actual = _leaves(output)
                expected_types, actual_types = _containers(case["expected"]), _containers(output)
                wrong_containers = {path for path in expected_types.keys() & actual_types.keys()
                                    if expected_types[path] is not actual_types[path]}
            except (KeyError, ValueError, RecursionError):
                status = "invalid_output"
        missing = sorted(expected.keys() - actual.keys())
        unexpected = sorted(actual.keys() - expected.keys())
        mismatched = sorted(path for path in expected.keys() & actual.keys()
                            if not _equal(expected[path], actual[path])
                            or any(path == parent or path.startswith(parent + "/")
                                   for parent in wrong_containers))
        matched = len(expected) - len(missing) - len(mismatched)
        passed = status == "ok" and not (missing or unexpected or mismatched)
        results.append({"id": case_id, "status": status, "passed": passed,
                        "expected_fields": len(expected), "matched_fields": matched,
                        "missing": missing, "unexpected": unexpected, "mismatched": mismatched})
    expected_count = sum(item["expected_fields"] for item in results)
    matched_count = sum(item["matched_fields"] for item in results)
    return {"schema_version": 1, "cases": results, "summary": {
        "case_count": len(results), "passed_cases": sum(item["passed"] for item in results),
        "expected_fields": expected_count, "matched_fields": matched_count,
        "field_accuracy": matched_count / expected_count,
        "unexpected_fields": sum(len(item["unexpected"]) for item in results),
        "passed": all(item["passed"] for item in results),
    }}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", type=Path, required=True, help="Reference JSONL: id, expected")
    parser.add_argument("--predictions", type=Path, required=True, help="Prediction JSONL: id, output")
    parser.add_argument("--report", type=Path, help="Optional JSON report file; also printed to stdout")
    args = parser.parse_args(argv)
    try:
        report = evaluate(read_records(args.cases), read_records(args.predictions))
        rendered = json.dumps(report, indent=2, ensure_ascii=True, allow_nan=False) + "\n"
        if args.report:
            args.report.write_text(rendered, encoding="utf-8")
        print(rendered, end="")
        return 0 if report["summary"]["passed"] else 1
    except (OSError, ValueError, TypeError, RecursionError) as exc:
        print(f"Evaluation input/report error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
