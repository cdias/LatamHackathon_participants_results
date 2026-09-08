"""
Ask the Airport - live judging dashboard (table layout, official rubric).

Paste each squad's repo URL, click "Analyze". Criteria are transcribed
verbatim from the official guide's "How points work" section (Part A =
judged live from the demo, Part B = verified by AI from the public repo).
Part B fields are pre-filled from static evidence in the repo; everything
stays editable.

Run with:
    source venv/bin/activate && streamlit run dashboard_app.py
"""
import json
import shutil
import tempfile
from pathlib import Path

import time

import streamlit as st

import analysis_store as asrc
import voting_store as vs
from analyzer import analyze_repo, RUBRIC, GATE_REQUIREMENTS

st.set_page_config(page_title="Ask the Airport — Judging Dashboard", layout="wide")

ALL_CRITERIA = [
    (part_key, part["title"], crit)
    for part_key, part in RUBRIC.items()
    for crit in part["criteria"]
]
MAX_TOTAL = sum(part["max"] for part in RUBRIC.values())


def parse_squads(raw_text):
    squads = []
    for line in raw_text.splitlines():
        line = line.strip()
        if not line or "," not in line:
            continue
        name, url = line.split(",", 1)
        squads.append((name.strip(), url.strip()))
    return squads


def run_analysis(squads, progress_cb=None):
    results = []
    tmp_root = Path(tempfile.mkdtemp(prefix="hackathon_dashboard_"))
    try:
        for i, (squad, url) in enumerate(squads):
            dest = tmp_root / f"repo_{i}"
            try:
                result = analyze_repo(url, dest, log=lambda m: None)
                result["squad"] = squad
                result["error"] = None
            except Exception as e:
                result = {"squad": squad, "url": url, "error": str(e)}
            results.append(result)
            if progress_cb:
                progress_cb((i + 1) / len(squads), squad)
    finally:
        shutil.rmtree(tmp_root, ignore_errors=True)
    return results


def score_key(squad, crit_key):
    return f"score_{squad}_{crit_key}"


def init_defaults(results):
    for r in results:
        if r.get("error"):
            continue
        judge_avg = vs.team_average(r["squad"])
        for crit in RUBRIC["part_a"]["criteria"]:
            default = 0
            if judge_avg["n"]:
                default = round(judge_avg["per_criterion"].get(crit["key"], 0))
            st.session_state.setdefault(score_key(r["squad"], crit["key"]), default)
        suggested = r["part_b_suggested"]
        for crit in RUBRIC["part_b"]["criteria"]:
            st.session_state.setdefault(
                score_key(r["squad"], crit["key"]), suggested.get(crit["key"], 0)
            )


def squad_total(squad):
    total = 0
    for _, _, crit in ALL_CRITERIA:
        total += st.session_state.get(score_key(squad, crit["key"]), 0)
    return total


def gate_status(r):
    structural = r["structural"]
    evidence = r["evidence"]
    return [
        ("A public GitHub repository", True),  # implied: we cloned it from GitHub
        ("A SUBMISSION.md at the root of the repository", structural["has_submission_md_at_root"]),
        ("TiDB used somewhere in your application", bool(evidence.get("tidb_used"))),
        ("A working demo of up to 2 minutes", None),  # can't verify statically
    ]


# ---------- Streamlit UI ----------

st.title("🛫 Ask the Airport — Judging Dashboard")
st.caption("TiDB × AWS Hackathon — São Paulo, 2026-09-02 · criteria from the official guide")

with st.expander("How to use", expanded="results" not in st.session_state):
    st.markdown(
        "1. Paste one line per squad: `Squad Name,https://github.com/...`\n"
        "2. Click **Analyze** — repos are cloned read-only (never executed) and deleted afterward\n"
        "3. **Part A** (60 pts, live at the demo) is left blank for you to fill in\n"
        "4. **Part B** (40 pts, verified from the repo) comes pre-filled from static evidence — adjust if something turns out to be dead/unused code\n"
        "5. Click **Save Part B results** and see the combined score on the **Final Results** page "
        "(sidebar), which also has the HTML export button"
    )

# ---------- Live judge voting (Part A) ----------

st.header("🗳️ Live judge voting")
st.caption(
    "Send the \"Judge Voting\" link (in the sidebar, or "
    f"`http://<your-wifi-ip>:8501/Judge_Voting`) to the judges. "
    "Votes are saved to `votes_data.json`, in this same folder — nothing goes to the cloud."
)

vote_data = vs.load_data()

with st.expander("Configure teams for voting", expanded=not vote_data.get("teams")):
    groups_path = Path(__file__).parent / "groups.json"
    if groups_path.exists():
        try:
            groups_data = json.loads(groups_path.read_text(encoding="utf-8"))
            group_names = [g["group"] for g in groups_data if g.get("group")]
        except Exception:
            groups_data, group_names = [], []
        if group_names:
            st.caption(
                f"Found `groups.json` with {len(group_names)} group(s) "
                f"({sum(len(g.get('members', [])) for g in groups_data)} people total)."
            )
            if st.button("📥 Load generated groups (groups.json)"):
                vs.set_teams(group_names)
                st.success(f"{len(group_names)} group(s) loaded as teams. Reloading...")
                st.rerun()
            with st.popover("View members of each group"):
                for g in groups_data:
                    members = ", ".join(m.get("name", "?") for m in g.get("members", []))
                    st.markdown(f"**{g['group']}** — {members}")
            st.divider()
    else:
        st.caption(
            "No `groups.json` found yet — generate groups from the check-in "
            "spreadsheet (see `generate_groups.py`) or type the teams manually below."
        )

    teams_text = st.text_area(
        "One team per line, in presentation order",
        value="\n".join(vote_data.get("teams", [])),
        height=140,
        key="voting_teams_text",
    )
    if st.button("Save team list"):
        names = [t.strip() for t in teams_text.splitlines() if t.strip()]
        vs.set_teams(names)
        st.success(f"{len(names)} team(s) saved. Reloading...")
        st.rerun()

teams_for_voting = vote_data.get("teams", [])
if teams_for_voting:
    auto_refresh = st.checkbox("Auto-refresh every 5s (during presentations)")

    ranking = sorted(
        [(t, vs.team_average(t)) for t in teams_for_voting],
        key=lambda kv: kv[1]["total_avg"],
        reverse=True,
    )

    st.subheader("Live scoreboard (Part A — 60 pts)")
    st.table(
        [
            {
                "Rank": i + 1,
                "Team": t,
                "Average": f"{avg['total_avg']:.1f} / {vs.MAX_TOTAL}" if avg["n"] else "— no votes —",
                "Judges": avg["n"],
            }
            for i, (t, avg) in enumerate(ranking)
        ]
    )

    with st.expander("Detail by team"):
        for t, avg in ranking:
            st.markdown(f"**{t}** — {avg['n']} vote(s)" + (f", judges: {', '.join(avg['judges'])}" if avg["judges"] else ""))
            if avg["n"]:
                crit_cols = st.columns(len(vs.CRITERIA))
                for col, crit in zip(crit_cols, vs.CRITERIA):
                    col.metric(crit["label"], f"{avg['per_criterion'][crit['key']]:.1f} / {crit['max']}")
            st.markdown("---")

    if auto_refresh:
        time.sleep(5)
        st.rerun()
else:
    st.info("Configure the team list above before sending the link to the judges.")

st.divider()
st.header("🧾 Repository analysis (Part B)")

raw_text = st.text_area(
    "Squads (one per line: Name,Repository URL)",
    height=120,
    placeholder="Squad A,https://github.com/team-a/project\nSquad B,https://github.com/team-b/project",
)

if st.button("🔍 Analyze", type="primary"):
    squads = parse_squads(raw_text)
    if not squads:
        st.warning("Paste at least one line in the format Name,URL.")
    else:
        progress = st.progress(0.0, text="Starting...")

        def cb(frac, squad):
            progress.progress(frac, text=f"Analyzing {squad}...")

        new_results = run_analysis(squads, progress_cb=cb)

        # Real bug from event day: st.session_state.setdefault() only sets the value
        # the first time. If these team names already had a score from a previous
        # analysis (a test, or an earlier round in the same browser session), clicking
        # "Analyze" again wouldn't update anything — it stayed stuck on the old value,
        # sometimes the same for several teams. So we clear these teams' scores
        # before reinitializing, forcing the new values to actually take effect.
        for r in new_results:
            for crit in RUBRIC["part_a"]["criteria"] + RUBRIC["part_b"]["criteria"]:
                st.session_state.pop(score_key(r["squad"], crit["key"]), None)

        st.session_state["results"] = new_results
        progress.empty()

if "results" in st.session_state:
    results = st.session_state["results"]
    init_defaults(results)
    valid_results = [r for r in results if not r.get("error")]

    for r in results:
        if r.get("error"):
            st.error(f"**{r['squad']}** — could not analyze: {r['error']}")

    # Gate warnings
    for r in valid_results:
        missing = [label for label, ok in gate_status(r) if ok is False]
        if missing:
            st.warning(f"**{r['squad']}** does not (yet) meet: " + "; ".join(missing))

    st.divider()

    # ---- The scoring table ----
    squads = [r["squad"] for r in valid_results]
    header_cols = st.columns([3, 3, 1] + [1.2] * len(squads))
    header_cols[0].markdown("**Criterion**")
    header_cols[1].markdown("**How it's judged**")
    header_cols[2].markdown("**Max.**")
    for col, squad in zip(header_cols[3:], squads):
        col.markdown(f"**{squad}**")

    for part_key, part in RUBRIC.items():
        st.markdown(f"##### {part['title']} — {part['subtitle']} ({part['max']} pts)")
        for crit in part["criteria"]:
            row_cols = st.columns([3, 3, 1] + [1.2] * len(squads))
            row_cols[0].markdown(f"**{crit['label']}**")
            row_cols[1].caption(crit["description"])
            row_cols[2].markdown(f"{crit['max']}")
            for col, r in zip(row_cols[3:], valid_results):
                col.number_input(
                    " ",
                    min_value=0,
                    max_value=crit["max"],
                    key=score_key(r["squad"], crit["key"]),
                    label_visibility="collapsed",
                )
            if part_key == "part_a":
                judge_cols = st.columns([3, 3, 1] + [1.2] * len(squads))
                for col, r in zip(judge_cols[3:], valid_results):
                    avg = vs.team_average(r["squad"])
                    if avg["n"]:
                        col.caption(
                            f"👥 judges: {avg['per_criterion'].get(crit['key'], 0):.1f} "
                            f"({avg['n']} vote{'s' if avg['n'] != 1 else ''})"
                        )
                    else:
                        col.caption("👥 no votes yet")
            if crit["key"] == "works":
                signal_cols = st.columns([3, 3, 1] + [1.2] * len(squads))
                signal_cols[1].caption(
                    "Static signal only — not a substitute for the demo. "
                    "Code can parse cleanly and still fail at runtime."
                )
                for col, r in zip(signal_cols[3:], valid_results):
                    health = r.get("code_health", {})
                    errors = health.get("syntax_errors", [])
                    stubs = health.get("stub_markers", [])
                    lines = health.get("code_lines", 0)
                    if errors:
                        col.caption(f"❌ {len(errors)} syntax error(s)")
                    elif lines < 30:
                        col.caption(f"⚠️ only {lines} lines of code")
                    elif stubs:
                        col.caption(f"✅ parses · ⚠️ {len(stubs)} pending stub(s)")
                    else:
                        col.caption(f"✅ parses · {lines} lines")
        st.markdown("---")

    st.divider()

    if st.button("💾 Save Part B results (analysis_data.json)"):
        for r in valid_results:
            part_b_scores = {
                crit["key"]: st.session_state.get(score_key(r["squad"], crit["key"]), 0)
                for crit in RUBRIC["part_b"]["criteria"]
            }
            asrc.save_result(r["squad"], r["url"], part_b_scores)
        st.success(
            f"Part B saved for {len(valid_results)} team(s) in `analysis_data.json` — "
            "independent of judge voting. See the combined scoreboard on "
            "**Final Results** (sidebar)."
        )

    st.divider()

    # ---- Final leaderboard, descending ----
    st.subheader("🏆 Final ranking")
    totals = {r["squad"]: squad_total(r["squad"]) for r in valid_results}
    ranking = sorted(totals.items(), key=lambda kv: kv[1], reverse=True)
    st.table(
        [{"Rank": i + 1, "Squad": squad, "Points": f"{total} / {MAX_TOTAL}"}
         for i, (squad, total) in enumerate(ranking)]
    )
    st.caption("To export an HTML to project on screen, use the **Final Results** page (sidebar) — "
               "it combines Part A + Part B directly from the saved files.")

