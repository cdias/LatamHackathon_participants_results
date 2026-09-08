"""
Local, file-based store for Part B repo-analysis results (40 pts).

Mirrors voting_store.py's pattern exactly, but for the "Verified by AI from
your public repository" side of the rubric. Kept independent of
votes_data.json on purpose — you can save Part B results whenever a repo
analysis is done, regardless of whether judges have voted yet.
"""
import fcntl
import json
from contextlib import contextmanager
from pathlib import Path

DATA_FILE = Path(__file__).parent / "analysis_data.json"

DEFAULT_DATA = {}  # {team_name: {url, scores: {crit_key: value}, total}}


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


def save_result(team, url, scores):
    data = load_data()
    data[team] = {
        "url": url,
        "scores": scores,
        "total": sum(scores.values()),
    }
    save_data(data)


def get_result(team):
    return load_data().get(team)


def all_results():
    return load_data()
