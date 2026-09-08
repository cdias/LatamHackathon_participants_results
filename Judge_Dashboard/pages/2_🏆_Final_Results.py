"""
Final Results — reads only the two local JSON files (votes_data.json +
analysis_data.json) and shows the combined 100-point scoreboard. Doesn't
depend on any analysis running in the session — this page can be opened
at any time, even after restarting Streamlit, as long as both files exist.
"""
import html
from pathlib import Path

import streamlit as st

import analysis_store as asrc
import voting_store as vs
from analyzer import RUBRIC

st.set_page_config(page_title="Ask the Airport — Final Results", layout="wide")

EXPORT_PATH = Path(__file__).parent.parent / "resultado_final.html"


def render_html(rows, analysis_data):
    def esc(s):
        return html.escape(str(s))

    ranking_rows = "\n".join(
        f"<tr><td>{i + 1}</td><td>{esc(r['team'])}</td>"
        f"<td>{r['part_a_total']:.1f} / 60</td>"
        f"<td>{r['part_b_total'] if r['part_b_done'] else '—'} / 40</td>"
        f"<td>{r['total']:.1f} / 100</td></tr>"
        for i, r in enumerate(rows)
    )

    cards = []
    for r in rows:
        part_b = analysis_data.get(r["team"])
        part_a_rows = "".join(
            f"<tr><td>{esc(c['label'])}</td><td>{c['max']}</td></tr>"
            for c in RUBRIC["part_a"]["criteria"]
        )
        part_b_rows = ""
        if part_b:
            crit_by_key = {c["key"]: c for c in RUBRIC["part_b"]["criteria"]}
            part_b_rows = "".join(
                f"<tr><td>{esc(crit_by_key[k]['label'] if k in crit_by_key else k)}</td>"
                f"<td>{v} / {crit_by_key[k]['max'] if k in crit_by_key else '?'}</td></tr>"
                for k, v in part_b["scores"].items()
            )
        cards.append(f"""
        <div class="card">
          <h3>{esc(r['team'])} <span class="total">{r['total']:.1f} / 100</span></h3>
          <div class="cols">
            <div>
              <h4>Part A — {r['part_a_total']:.1f} / 60 ({r['part_a_n']} vote{'s' if r['part_a_n'] != 1 else ''})</h4>
              <table>{part_a_rows}</table>
            </div>
            <div>
              <h4>Part B — {r['part_b_total'] if r['part_b_done'] else '— no analysis —'} / 40</h4>
              {f'<p class="url">{esc(part_b["url"])}</p>' if part_b else ''}
              <table>{part_b_rows or '<tr><td colspan="2">No analysis saved</td></tr>'}</table>
            </div>
          </div>
        </div>
        """)

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Ask the Airport — Final Results</title>
<style>
  :root {{
    --bg: #0f1117; --card: #1a1d29; --text: #e8e8f0; --muted: #9494a8;
    --accent: #4f9dff; --off: #3a3d4a;
  }}
  body {{ background: var(--bg); color: var(--text); font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 0; padding: 2rem; }}
  h1 {{ font-size: 2rem; margin-bottom: 0; }}
  .subtitle {{ color: var(--muted); margin-top: 0.25rem; margin-bottom: 2rem; }}
  table {{ border-collapse: collapse; width: 100%; margin-bottom: 1rem; }}
  th, td {{ padding: 0.5rem 0.8rem; border-bottom: 1px solid var(--off); text-align: left; font-size: 0.9rem; }}
  th {{ color: var(--muted); font-weight: 600; }}
  table.ranking tr:nth-child(1) td {{ color: gold; font-weight: bold; }}
  table.ranking tr:nth-child(2) td {{ color: silver; }}
  table.ranking tr:nth-child(3) td {{ color: #cd7f32; }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(420px, 1fr)); gap: 1.2rem; }}
  .card {{ background: var(--card); border-radius: 12px; padding: 1.2rem 1.4rem; }}
  .card h3 {{ margin-top: 0; display: flex; justify-content: space-between; align-items: center; }}
  .total {{ color: var(--accent); font-size: 1rem; }}
  .card h4 {{ font-size: 0.85rem; color: var(--muted); margin-bottom: 0.4rem; }}
  .cols {{ display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }}
  .url {{ font-size: 0.75rem; color: var(--muted); word-break: break-all; }}
</style>
</head>
<body>
  <h1>🛫 Ask the Airport</h1>
  <p class="subtitle">Final Results — TiDB × AWS Hackathon, São Paulo, 2026-09-02</p>

  <h2>🏆 Ranking</h2>
  <table class="ranking">
    <tr><th>Rank</th><th>Team</th><th>Part A</th><th>Part B</th><th>Total</th></tr>
    {ranking_rows}
  </table>

  <h2>Detail by team</h2>
  <div class="grid">
    {"".join(cards)}
  </div>
</body>
</html>"""

st.title("🏆 Final Results")
st.caption("Part A (60 pts, judge voting) + Part B (40 pts, repository analysis) = 100 pts")

if st.button("🔄 Refresh"):
    st.rerun()

vote_data = vs.load_data()
teams = vote_data.get("teams", [])
analysis_data = asrc.all_results()

all_team_names = list(dict.fromkeys(list(teams) + list(analysis_data.keys())))

if not all_team_names:
    st.info(
        "No teams configured yet and no results saved. "
        "Configure the teams on the main page and/or save the Part B analysis first."
    )
    st.stop()

rows = []
for team in all_team_names:
    part_a = vs.team_average(team)
    part_a_total = part_a["total_avg"] if part_a["n"] else 0.0
    part_b = analysis_data.get(team)
    part_b_total = part_b["total"] if part_b else 0
    rows.append({
        "team": team,
        "part_a_total": part_a_total,
        "part_a_n": part_a["n"],
        "part_b_total": part_b_total,
        "part_b_done": part_b is not None,
        "total": part_a_total + part_b_total,
    })

rows.sort(key=lambda r: r["total"], reverse=True)

st.subheader("Overall scoreboard")
st.table([
    {
        "Rank": i + 1,
        "Team": r["team"],
        "Part A (60)": f"{r['part_a_total']:.1f}" if r["part_a_n"] else "— no votes —",
        "Judges": r["part_a_n"],
        "Part B (40)": r["part_b_total"] if r["part_b_done"] else "— no analysis —",
        "Total (100)": f"{r['total']:.1f}",
    }
    for i, r in enumerate(rows)
])

missing_a = [r["team"] for r in rows if not r["part_a_n"]]
missing_b = [r["team"] for r in rows if not r["part_b_done"]]
if missing_a:
    st.warning(f"No judge votes yet: {', '.join(missing_a)}")
if missing_b:
    st.warning(f"No Part B analysis saved yet: {', '.join(missing_b)}")

with st.expander("Detail by team"):
    for r in rows:
        st.markdown(f"### {r['team']} — {r['total']:.1f} / 100")
        cols = st.columns(2)
        cols[0].metric("Part A (judges)", f"{r['part_a_total']:.1f} / 60", f"{r['part_a_n']} vote(s)")
        cols[1].metric("Part B (repository)", f"{r['part_b_total']} / 40")
        part_b = analysis_data.get(r["team"])
        if part_b:
            st.caption(f"Repository analyzed: {part_b['url']}")
            for crit_key, val in part_b["scores"].items():
                st.caption(f"- {crit_key}: {val}")
        st.divider()

if st.button("💾 Export HTML to project on screen"):
    html_content = render_html(rows, analysis_data)
    EXPORT_PATH.write_text(html_content, encoding="utf-8")
    st.success(f"Saved to {EXPORT_PATH}")
    st.download_button(
        "Download resultado_final.html", html_content, file_name="resultado_final.html", mime="text/html"
    )
