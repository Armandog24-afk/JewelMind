"""Developer/CI workflow for Golden Models (QUALITY-GOV-003/004/018, see
docs/bible/17-geometry-quality/507-golden-update-policy.md):

    python -m jewelmind.geometry_quality.cli verify-all
    python -m jewelmind.geometry_quality.cli verify SOL-001-default-solitaire
    python -m jewelmind.geometry_quality.cli generate-candidate SOL-001-default-solitaire
    python -m jewelmind.geometry_quality.cli diff SOL-001-default-solitaire
    python -m jewelmind.geometry_quality.cli accept SOL-001-default-solitaire --reason "..."

`accept` is the ONLY command that writes to an accepted baseline
(`snapshot.json`) and it always requires an explicit `--reason`. No other
command — and no CI invocation of any command here — ever does.
"""

from __future__ import annotations

import argparse
import sys

from jewelmind.geometry_quality.compare import compare_snapshot
from jewelmind.geometry_quality.harness import (
    accept_candidate_baseline,
    generate_candidate_baseline,
    verify_all_goldens,
    verify_golden,
)
from jewelmind.geometry_quality.registry import load_candidate, load_golden, save_candidate


def _cmd_verify_all(args: argparse.Namespace) -> int:
    results = verify_all_goldens(check_artifacts=args.artifacts)
    failed = [r for r in results if r.status not in ("PASS", "PASS_WITH_KNOWN_LIMITATIONS")]
    for r in results:
        print(f"{r.goldenId}: {r.status}")
    if failed:
        print(f"\n{len(failed)} of {len(results)} golden(s) require attention.")
        for r in failed:
            print(f"\n{r.message}")
        return 1
    print(f"\nAll {len(results)} golden(s) PASS.")
    return 0


def _cmd_verify(args: argparse.Namespace) -> int:
    result = verify_golden(args.golden_id, check_artifacts=args.artifacts)
    print(result.message)
    return 0 if result.status in ("PASS", "PASS_WITH_KNOWN_LIMITATIONS") else 1


def _cmd_generate_candidate(args: argparse.Namespace) -> int:
    candidate = generate_candidate_baseline(args.golden_id)
    path = save_candidate(candidate)
    print(f"Candidate baseline written to {path}. Run 'diff' to review before 'accept'.")
    return 0


def _cmd_diff(args: argparse.Namespace) -> int:
    try:
        golden = load_golden(args.golden_id)
    except FileNotFoundError:
        print(f"No accepted baseline for '{args.golden_id}' — every fact in the candidate is new.")
        golden = None
    candidate = load_candidate(args.golden_id)
    if golden is None:
        print(candidate.model_dump_json(indent=2))
        return 0
    diff = compare_snapshot(
        args.golden_id,
        golden.geometrySnapshot,
        candidate.geometrySnapshot,
        golden.versionFingerprint,
        candidate.versionFingerprint,
    )
    print(diff.human_readable())
    return 0


def _cmd_accept(args: argparse.Namespace) -> int:
    candidate = load_candidate(args.golden_id)
    candidate = candidate.model_copy(update={"notes": f"{candidate.notes}\nReason: {args.reason}".strip()})
    accepted = accept_candidate_baseline(candidate)
    print(f"Accepted baseline for '{accepted.goldenId}' at {accepted.acceptedAt}. Reason: {args.reason}")
    print("Remember to record this in docs/bible/appendices/golden-update-register.md.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="geometry-quality")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("verify-all", help="Verify every golden in the suite against real geometry.")
    p.add_argument("--artifacts", action="store_true", help="Also run STEP/STL artifact regression.")
    p.set_defaults(func=_cmd_verify_all)

    p = sub.add_parser("verify", help="Verify one golden against real geometry.")
    p.add_argument("golden_id")
    p.add_argument("--artifacts", action="store_true")
    p.set_defaults(func=_cmd_verify)

    p = sub.add_parser("generate-candidate", help="Generate (never accept) a candidate baseline.")
    p.add_argument("golden_id")
    p.set_defaults(func=_cmd_generate_candidate)

    p = sub.add_parser("diff", help="Show the human-readable diff for a generated candidate.")
    p.add_argument("golden_id")
    p.set_defaults(func=_cmd_diff)

    p = sub.add_parser("accept", help="Explicitly promote a candidate to the accepted baseline.")
    p.add_argument("golden_id")
    p.add_argument("--reason", required=True, help="Why this baseline change is intentional and correct.")
    p.set_defaults(func=_cmd_accept)

    parsed = parser.parse_args(argv)
    return parsed.func(parsed)


if __name__ == "__main__":
    sys.exit(main())
