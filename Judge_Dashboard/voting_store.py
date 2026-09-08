"""
Local, file-based store for live Part A judge voting.

One JSON file (votes_data.json) shared by every Streamlit session on the
same machine/process. Judges hit the "Judge Voting" page over the venue
wifi (same laptop, different browsers/devices); the admin dashboard reads
this file to show live averages. A simple fcntl lock keeps concurrent
writes from a handful of judges from clobbering each other — this is not
built for heavy concurrency, just enough for ~5 judges voting on ~5-7 teams.
"""
import fcntl
import json
from contextlib import contextmanager
from pathlib import Path

DATA_FILE = Path(__file__).parent / "votes_data.json"

DEFAULT_DATA = {"teams": [], "votes": {}}  # votes: {team_name: {judge_name: {scores, total}}}

CRITERIA = [
    {"key": "works", "label": "It works", "max": 20},
    {"key": "innovation", "label": "Innovation and creativity", "max": 15},
    {"key": "business_value", "label": "Business value", "max": 15},
    {"key": "demo", "label": "Demo and pitch", "max": 10},
]
MAX_TOTAL = sum(c["max"] for c in CRITERIA)


@contextmanager
def _locked_file():
    DATA_FILE.touch(exist_ok=True)
    with open(DATA_FILE, "r+", encoding="utf-8") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        try:
            yield f
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)


def load_data():
    if not DATA_FILE.exists():
        return dict(DEFAULT_DATA)
    with _locked_file() as f:
        f.seek(0)
        content = f.read()
    if not content.strip():
        return dict(DEFAULT_DATA)
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return dict(DEFAULT_DATA)


def save_data(data):
    with _locked_file() as f:
        f.seek(0)
        f.truncate()
        json.dump(data, f, indent=2, ensure_ascii=False)


def set_teams(names):
    data = load_data()
    data["teams"] = names
    save_data(data)


def submit_vote(team, judge, scores):
    data = load_data()
    data.setdefault("votes", {})
    data["votes"].setdefault(team, {})
    data["votes"][team][judge] = {
        "scores": scores,
        "total": sum(scores.values()),
    }
    save_data(data)


def get_vote(team, judge):
    data = load_data()
    return data.get("votes", {}).get(team, {}).get(judge)


def judges_for_team(team):
    data = load_data()
    return list(data.get("votes", {}).get(team, {}).keys())


def team_average(team):
    data = load_data()
    entries = list(data.get("votes", {}).get(team, {}).values())
    n = len(entries)
    per_crit = {}
    for c in CRITERIA:
        per_crit[c["key"]] = (
            sum(e["scores"].get(c["key"], 0) for e in entries) / n if n else 0.0
        )
    total_avg = sum(e["total"] for e in entries) / n if n else 0.0
    judge_names = list(data.get("votes", {}).get(team, {}).keys())
    return {"n": n, "per_criterion": per_crit, "total_avg": total_avg, "judges": judge_names}


def my_votes(judge):
    """Every team this judge has already voted for, {team: total}."""
    data = load_data()
    out = {}
    for team, judges in data.get("votes", {}).items():
        if judge in judges:
            out[team] = judges[judge]["total"]
    return out
