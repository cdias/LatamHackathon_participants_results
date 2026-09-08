#!/usr/bin/env python3
"""
Ask the Airport - Hackathon judging helper (single repo, Markdown report).

Quick CLI alternative to dashboard_app.py for a one-off spot check on a
single repo. Uses the same official rubric (see analyzer.RUBRIC).

Usage:
    python judge_repo.py <git_url> [--squad "Squad Name"] [--keep]

Safety: read-only static analysis. Never installs or executes the cloned code.
"""
import argparse
import csv
import shutil
import tempfile
from pathlib import Path

from analyzer import analyze_repo, RUBRIC, GATE_REQUIREMENTS, CHECKS

REPORTS_DIR = Path(__file__).parent / "reports"
SCOREBOARD_CSV = Path(__file__).parent / "scoreboard.csv"


def render_report(squad, result):
    structural = result["structural"]
    evidence = result["evidence"]
    suggested = result["part_b_suggested"]
    lines = []
    lines.append(f"# Judging report — {squad or result['url']}")
    lines.append("")
    lines.append(f"**Repo:** {result['url']}")
    lines.append("")
    lines.append("> The Part B rows below come pre-filled with static evidence — check "
                  "that the code isn't dead/unused before trusting them. Part A can only "
                  "be judged live, during the demo.")
    lines.append("")

    lines.append("## Gate requirements (\"TO BE JUDGED, YOU NEED\")")
    lines.append("")
    lines.append(f"- A public GitHub repository: ✅ (cloned from GitHub)")
    lines.append(f"- A SUBMISSION.md at the root of the repository: "
                 f"{'✅' if structural['has_submission_md_at_root'] else '❌'}")
    lines.append(f"- TiDB used somewhere in your application: "
                 f"{'✅' if evidence.get('tidb_used') else '❌'}")
    lines.append(f"- A working demo of up to 2 minutes: ⬜ verify live")
    lines.append("")

    lines.append("## Scoreboard")
    lines.append("")
    lines.append("| Criterion | Max. | Automated signal | Score (fill in) |")
    lines.append("|---|---|---|---|")
    for part_key, part in RUBRIC.items():
        lines.append(f"| **{part['title']}** ({part['subtitle']}) | **{part['max']}** | | |")
        for crit in part["criteria"]:
            if crit.get("automatable"):
                found = bool(evidence.get(crit["evidence_key"]))
                signal = f"{'✅ found' if found else '❌ not found'} → suggests {suggested[crit['key']]}"
            elif crit["key"] == "works":
                health = result.get("code_health", {})
                errors = health.get("syntax_errors", [])
                stubs = health.get("stub_markers", [])
                lines_of_code = health.get("code_lines", 0)
                if errors:
                    signal = f"❌ {len(errors)} syntax error(s) — verify live"
                elif lines_of_code < 30:
                    signal = f"⚠️ only {lines_of_code} lines of code — verify live"
                elif stubs:
                    signal = f"✅ parses, {lines_of_code} lines, ⚠️ {len(stubs)} pending stub(s) — verify live"
                else:
                    signal = f"✅ parses, {lines_of_code} lines — verify live (static only, doesn't prove it runs)"
            else:
                signal = "manual only — judge live"
            lines.append(f"| {crit['label']} | {crit['max']} | {signal} | ___ |")
    lines.append(f"| **TOTAL** | **{sum(p['max'] for p in RUBRIC.values())}** | | **___** |")
    lines.append("")

    lines.append("## Raw evidence (file:line matches)")
    lines.append("")
    for key, spec in CHECKS.items():
        hits = evidence[key]
        status = "✅ FOUND" if hits else "❌ not found"
        lines.append(f"### {spec['label']} — {status}")
        for rel, note in hits[:5]:
            lines.append(f"- `{rel}` — {note}")
        if len(hits) > 5:
            lines.append(f"- ... +{len(hits) - 5} more match(es)")
        lines.append("")

    lines.append("## Structural sanity")
    lines.append(f"- Dependency manifest present: {'yes' if structural['has_manifest'] else 'NO'}")
    lines.append(f"- Recognizable entrypoint file: {'yes' if structural['has_entrypoint'] else 'NO'}")
    lines.append(f"- Commits (shallow clone, may be truncated): {result['commit_count']}")
    if result["contributors"]:
        lines.append(f"- Contributors: {', '.join(result['contributors'])}")
    lines.append("")
    return "\n".join(lines)


def append_scoreboard(squad, result):
    structural = result["structural"]
    evidence = result["evidence"]
    is_new = not SCOREBOARD_CSV.exists()
    with open(SCOREBOARD_CSV, "a", newline="") as f:
        writer = csv.writer(f)
        if is_new:
            writer.writerow([
                "squad", "repo_url", "has_submission_md_at_root", "has_manifest",
                "has_entrypoint", "commit_count", "tidb_used_evidence",
                "tidb_cloud_aws_evidence", "bedrock_evidence",
                "vector_search_evidence", "deployed_aws_evidence", "kiro_evidence",
            ])
        writer.writerow([
            squad or "", result["url"], structural["has_submission_md_at_root"],
            structural["has_manifest"], structural["has_entrypoint"],
            result["commit_count"], bool(evidence["tidb_used"]),
            bool(evidence["tidb_cloud_aws"]), bool(evidence["bedrock"]),
            bool(evidence["vector_search"]), bool(evidence["deployed_aws"]),
            bool(evidence["kiro"]),
        ])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("url")
    parser.add_argument("--squad", default="")
    parser.add_argument("--keep", action="store_true",
                         help="keep the cloned repo instead of deleting it")
    args = parser.parse_args()

    REPORTS_DIR.mkdir(exist_ok=True)
    tmp_root = Path(tempfile.mkdtemp(prefix="hackathon_judge_"))
    repo_name = args.url.rstrip("/").split("/")[-1].replace(".git", "")
    dest = tmp_root / repo_name

    try:
        result = analyze_repo(args.url, dest)
        report = render_report(args.squad, result)
        report_path = REPORTS_DIR / f"{repo_name}.md"
        report_path.write_text(report)
        append_scoreboard(args.squad, result)

        print(report)
        print(f"\nReport saved to {report_path}")
        print(f"Row added to {SCOREBOARD_CSV}")
    finally:
        if args.keep:
            print(f"Clone kept at {dest}")
        else:
            shutil.rmtree(tmp_root, ignore_errors=True)
            print(f"Temporary clone deleted at {tmp_root}")


if __name__ == "__main__":
    main()
