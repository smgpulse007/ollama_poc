import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from extraction_eval import evaluate, parse_json, read_records

ROOT = Path(__file__).resolve().parents[1]


def check(expected, output):
    return evaluate({"x": {"expected": expected}}, {"x": {"output": output}})


class EvaluationTests(unittest.TestCase):
    def test_exact_match_and_json_number_equivalence(self):
        self.assertTrue(check({"total": 18.0}, {"total": 18})["summary"]["passed"])

    def test_boolean_is_not_number(self):
        self.assertFalse(check({"total": 1}, {"total": True})["summary"]["passed"])

    def test_null_does_not_equal_absence(self):
        result = check({"due": None}, {})
        self.assertEqual(result["cases"][0]["missing"], ["/due"])

    def test_extra_fields_fail_even_with_full_expected_accuracy(self):
        result = check({"a": 1}, {"a": 1, "invented": "value"})
        self.assertEqual(result["summary"]["field_accuracy"], 1)
        self.assertFalse(result["summary"]["passed"])
        self.assertEqual(result["cases"][0]["unexpected"], ["/invented"])

    def test_nested_arrays_and_escaped_json_pointer(self):
        result = check({"a/b~": [{"c": 1}]}, {"a/b~": [{"c": 2}]})
        self.assertEqual(result["cases"][0]["mismatched"], ["/a~1b~0/0/c"])

    def test_array_order_matters(self):
        self.assertFalse(check({"a": [1, 2]}, {"a": [2, 1]})["summary"]["passed"])

    def test_object_with_numeric_key_is_not_array(self):
        result = check({"a": {"0": 1}}, {"a": [1]})
        self.assertEqual(result["cases"][0]["mismatched"], ["/a/0"])

    def test_empty_containers_and_string_numbers_differ(self):
        for expected, actual in (({}, []), ([], None), (2, "2")):
            self.assertFalse(check({"a": expected}, {"a": actual})["summary"]["passed"])

    def test_json_string_output(self):
        self.assertTrue(check({"a": 1}, '{"a": 1}')["summary"]["passed"])

    def test_invalid_outputs_fail_without_echoing_values(self):
        for output in ('not-json-private-text', '{"x": NaN}', '{"x":1,"x":2}', []):
            result = check({"a": "private-reference"}, output)
            self.assertEqual(result["cases"][0]["status"], "invalid_output")
            self.assertNotIn("private", json.dumps(result))

    def test_missing_prediction_counts_expected_fields(self):
        result = evaluate({"x": {"expected": {"a": 1, "b": 2}}}, {})
        self.assertEqual(result["summary"]["field_accuracy"], 0)
        self.assertEqual(result["cases"][0]["status"], "missing_prediction")

    def test_unknown_ids_and_empty_reference_rejected(self):
        with self.assertRaises(ValueError):
            evaluate({}, {})
        with self.assertRaises(ValueError):
            evaluate({"x": {"expected": {}}}, {"y": {"output": {}}})

    def test_duplicate_ids_and_malformed_jsonl_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "records.jsonl"
            for text in ('{"id":"a"}\n{"id":"a"}\n', '{broken}\n', '{"id":1}\n'):
                path.write_text(text, encoding="utf-8")
                with self.assertRaises(ValueError):
                    read_records(path)

    def test_strict_json_rejects_duplicate_keys_and_infinity(self):
        for text in ('{"a":1,"a":2}', '{"a":Infinity}', '{"a":NaN}'):
            with self.assertRaises(ValueError):
                parse_json(text)

    def test_distinct_large_json_numbers_do_not_round_to_a_match(self):
        result = check(parse_json('{"amount":9007199254740992}'),
                       parse_json('{"amount":9007199254740993.0}'))
        self.assertFalse(result["summary"]["passed"])

    def test_small_json_numbers_do_not_underflow_to_zero(self):
        result = check(parse_json('{"amount":0}'), parse_json('{"amount":1e-999}'))
        self.assertFalse(result["summary"]["passed"])

    def test_equivalent_decimal_and_exponent_forms_match_exactly(self):
        result = check(parse_json('{"amount":1e999,"tiny":1e-999,"value":18.00}'),
                       parse_json('{"amount":10e998,"tiny":10e-1000,"value":18}'))
        self.assertTrue(result["summary"]["passed"])

    def test_cli_fixtures_and_report(self):
        with tempfile.TemporaryDirectory() as directory:
            report = Path(directory) / "report.json"
            for suffix, expected_code, matched in (("pass", 0, 8), ("fail", 1, 7)):
                run = subprocess.run([
                    sys.executable, str(ROOT / "extraction_eval.py"),
                    "--cases", str(ROOT / "examples/eval/cases.jsonl"),
                    "--predictions", str(ROOT / f"examples/eval/predictions-{suffix}.jsonl"),
                    "--report", str(report),
                ], capture_output=True, text=True, timeout=15)
                self.assertEqual(run.returncode, expected_code, run.stderr)
                result = json.loads(run.stdout)
                self.assertEqual(result, json.loads(report.read_text()))
                self.assertEqual(result["summary"]["matched_fields"], matched)
                self.assertNotIn("source_text", run.stdout)

    def test_cli_input_errors_exit_two(self):
        run = subprocess.run([
            sys.executable, str(ROOT / "extraction_eval.py"),
            "--cases", str(ROOT / "does-not-exist.jsonl"),
            "--predictions", str(ROOT / "examples/eval/predictions-pass.jsonl"),
        ], capture_output=True, text=True, timeout=15)
        self.assertEqual(run.returncode, 2)


if __name__ == "__main__":
    unittest.main()
