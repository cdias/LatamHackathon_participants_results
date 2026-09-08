# Ask the Airport — Judge Dashboard

A live judging dashboard for hackathon events. Judges vote live on **Part A**
(what the team built — 60 pts) from a shared voting page, while organizers
run automated static analysis on each team's repo for **Part B** (how it
was built — 40 pts). Both feed into one combined 100-point ranking.

Built for the "Ask the Airport" TiDB × AWS Hackathon, but the scoring
mechanics are generic enough to reuse for other events (swap the rubric in
`analyzer.py` and `voting_store.py`).

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Running

Start the dashboard so it's reachable by judges over the venue wifi (not
just `localhost`):

```bash
streamlit run dashboard_app.py --server.address 0.0.0.0 --server.port 8503
```

Find your machine's LAN IP and share the Judge Voting page link with the
judges, e.g. `http://<your-ip>:8503/Judge_Voting`. You can bake a judge's
name into the URL to save them retyping it: `.../Judge_Voting?judge=Camila`.

## Pages

- **Main dashboard** (`dashboard_app.py`) — the organizer's admin view.
  Configure the team list, watch the live Part A voting results come in,
  and run repo analysis for Part B (paste `Name,repo URL` pairs, click
  Analyze). Part B scores are pre-filled from static evidence but stay
  editable before saving.
- **Judge Voting** (`pages/1_🗳️_Judge_Voting.py`) — the judge-facing page.
  A judge enters their name, picks the team presenting, and scores the four
  Part A criteria (It works / Innovation and creativity / Business value /
  Demo and pitch). One vote per judge per team; resubmitting overwrites it.
- **Final Results** (`pages/2_🏆_Final_Results.py`) — combines Part A
  (judge vote averages) and Part B (saved repo-analysis scores) into a
  single 100-point ranking. Reads directly from the two JSON files, so it
  works even after a Streamlit restart, and it can export a standalone
  HTML page to project on screen.

## Data

Everything is local JSON, no cloud dependency:
- `votes_data.json` — judge votes (Part A)
- `analysis_data.json` — saved repo-analysis scores (Part B)
- `groups.json` (optional) — pre-generated team list, if you have one

## Safety

Repository analysis (`analyzer.py`, `judge_repo.py`) is **read-only static
analysis**: it clones each repo shallowly, scans file contents/paths for
rubric evidence with regex, and deletes the clone afterward. It never
installs dependencies and never executes any code from the cloned repos.
