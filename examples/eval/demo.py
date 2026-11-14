"""Run the evaluator against hand-written passing and failing synthetic fixtures."""
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[2]


def main():
    print("Synthetic extraction regression demo -- no model is called.\n")
    for fixture, expected_exit in [("pass", 0), ("fail", 1)]:
        args = [sys.executable, "extraction_eval.py", "--cases", "examples/eval/cases.jsonl",
                "--predictions", f"examples/eval/predictions-{fixture}.jsonl"]
        result = subprocess.run(args, cwd=ROOT, capture_output=True, text=True, timeout=30)
        if result.returncode != expected_exit:
            raise RuntimeError(f"Unexpected exit for {fixture} fixture: {result.returncode}\n{result.stderr}")
        report = json.loads(result.stdout)
        summary = report["summary"]
        print(f"{fixture.upper()} fixture | exit {result.returncode}")
        print(f"  Cases passed: {summary['passed_cases']}/{summary['case_count']}")
        print(f"  Reference fields matched: {summary['matched_fields']}/{summary['expected_fields']}")
        print(f"  Unexpected fields: {summary['unexpected_fields']}")
        for case in report["cases"]:
            for kind in ("missing", "mismatched", "unexpected"):
                for path in case[kind]:
                    print(f"  {case['id']}: {kind} {path}")
        print()
    print("The failing fixture is caught as intended. These are not model accuracy results.")


if __name__ == "__main__":
    main()
