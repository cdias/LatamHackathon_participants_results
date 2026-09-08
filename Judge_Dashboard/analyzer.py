"""
Shared static-analysis core for the "Ask the Airport" hackathon judging tools.

Clones a repo shallowly (read-only), scans file contents for rubric
evidence, then the caller is responsible for deleting the clone.
Never installs dependencies or executes the cloned code.

RUBRIC below is transcribed verbatim (labels, points, descriptions) from the
official "Ask the Airport.pdf" guide (TiDB x AWS Hackathon, 2026-09-02),
Drive file id 1MntkxfYgM884ODao79zjBikfHKLwJXu7, pages 3-4 ("How points work").
Total: 100 pts = Part A (60, judged live from the demo) + Part B (40,
verified by AI from the public repo).
"""
import ast
import os
import re
import subprocess
from pathlib import Path

TEXT_EXTENSIONS = {
    ".py", ".js", ".ts", ".tsx", ".jsx", ".java", ".go", ".rb", ".php",
    ".sql", ".md", ".yml", ".yaml", ".json", ".toml", ".cfg", ".ini",
    ".env", ".txt", ".sh", ".tf", ".dockerfile", "",
}

RUBRIC = {
    "part_a": {
        "title": "Part A — What you built",
        "subtitle": "Judged live at your demo",
        "max": 60,
        "criteria": [
            {
                "key": "works",
                "label": "It works",
                "max": 20,
                "description": "The thing runs and does what you say it does. "
                                "A rough app that works beats a pretty one that doesn't.",
                "automatable": False,
            },
            {
                "key": "innovation",
                "label": "Innovation and creativity",
                "max": 15,
                "description": "An angle we haven't seen four times today. Surprise us.",
                "automatable": False,
            },
            {
                "key": "business_value",
                "label": "Business value",
                "max": 15,
                "description": "Who has this problem, and is this a real answer for them? Name the user.",
                "automatable": False,
            },
            {
                "key": "demo",
                "label": "Demo and pitch",
                "max": 10,
                "description": "Two minutes, one clear story. Show the thing working "
                                "instead of just describing it.",
                "automatable": False,
            },
        ],
    },
    "part_b": {
        "title": "Part B — How you built it",
        "subtitle": "Verified by AI from your public repository",
        "max": 40,
        "criteria": [
            {
                "key": "tidb_cloud_aws",
                "label": "TiDB Cloud Starter on AWS",
                "max": 10,
                "description": "Your data lives in a TiDB Cloud cluster on AWS São Paulo "
                                "(sa-east-1). Running TiDB locally still keeps you "
                                "eligible — it just doesn't score points here.",
                "automatable": True,
                "evidence_key": "tidb_cloud_aws",
            },
            {
                "key": "vector_search",
                "label": "TiDB vector search",
                "max": 8,
                "description": "A VECTOR column queried with VEC_COSINE_DISTANCE, or the "
                                "EMBED_TEXT auto-embedding function. Either one counts.",
                "automatable": True,
                "evidence_key": "vector_search",
            },
            {
                "key": "bedrock",
                "label": "Amazon Bedrock",
                "max": 8,
                "description": "Used for text generation, embeddings, or both. Any other "
                                "LLM API keeps you fully eligible — it just doesn't score these 8.",
                "automatable": True,
                "evidence_key": "bedrock",
            },
            {
                "key": "deployed_aws",
                "label": "Deployed on AWS",
                "max": 8,
                "description": "Lambda with a Function URL, Amplify, Lightsail, EC2, ECS — "
                                "anything reachable by a URL. Running on your laptop is fine; "
                                "it just scores zero here.",
                "automatable": True,
                "evidence_key": "deployed_aws",
            },
            {
                "key": "kiro",
                "label": "Built with Kiro",
                "max": 6,
                "description": "Commit your specs and steering files under .kiro/ so we can see "
                                "the spec-driven work, not just the result.",
                "automatable": True,
                "evidence_key": "kiro",
            },
        ],
    },
}

GATE_REQUIREMENTS = [
    "A public GitHub repository",
    "A SUBMISSION.md at the root of the repository",
    "TiDB used somewhere in your application",
    "A working demo of up to 2 minutes",
]

CHECKS = {
    "tidb_used": {
        "label": "TiDB used somewhere (gate requirement)",
        "patterns": [
            r"tidb", r"TIDB_HOST", r"pymysql", r"mysql\.connector",
            r"mysql2", r"ssl[-_]mode", r"tidbcloud",
        ],
    },
    "tidb_cloud_aws": {
        "label": "TiDB Cloud Starter on AWS (sa-east-1)",
        "patterns": [
            r"tidbcloud\.com", r"\.clusters\.tidb-cloud\.com", r"sa-east-1",
        ],
    },
    "bedrock": {
        "label": "Amazon Bedrock",
        "patterns": [
            r"bedrock", r"invoke_model", r"anthropic\.claude",
            r"boto3\.client\(\s*[\"']bedrock",
        ],
    },
    "vector_search": {
        "label": "TiDB vector search",
        "patterns": [
            r"VEC_COSINE_DISTANCE", r"VEC_EMBED_COSINE_DISTANCE",
            r"EMBED_TEXT", r"VECTOR\(", r"fts_match_word",
        ],
    },
    "deployed_aws": {
        "label": "Deployed on AWS (Lambda/Amplify/Lightsail/EC2/ECS)",
        "patterns": [
            r"lambda", r"function[_-]?url", r"amplify", r"lightsail",
            r"\becs\b", r"\bec2\b", r"serverless\.ya?ml", r"template\.ya?ml",
            r"sam\.ya?ml", r"cloudformation",
        ],
    },
    "kiro": {
        "label": "Built with Kiro",
        "patterns": [r"\.kiro/"],
    },
}

ENTRYPOINT_NAMES = {
    "app.py", "main.py", "server.py", "manage.py", "index.js",
    "index.ts", "app.js", "server.js",
}


def run(cmd, cwd=None):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=False)


def clone_repo(url, dest, log=print):
    log(f"Cloning (shallow, read-only) {url} ...")
    result = run(["git", "clone", "--depth", "1", url, str(dest)])
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or f"git clone failed for {url}")


def walk_files(root):
    for dirpath, dirnames, filenames in os.walk(root):
        if ".git" in dirnames:
            dirnames.remove(".git")
        for name in filenames:
            yield Path(dirpath) / name


def collect_evidence(root):
    evidence = {key: [] for key in CHECKS}
    file_list = list(walk_files(root))

    for path in file_list:
        rel = path.relative_to(root).as_posix()
        for key, spec in CHECKS.items():
            for pat in spec["patterns"]:
                if re.search(pat, rel, re.IGNORECASE):
                    evidence[key].append((rel, f"path matches /{pat}/"))
                    break

    for path in file_list:
        rel = path.relative_to(root).as_posix()
        if path.suffix.lower() not in TEXT_EXTENSIONS and path.suffix != "":
            continue
        try:
            text = path.read_text(errors="ignore")
        except Exception:
            continue
        for key, spec in CHECKS.items():
            for pat in spec["patterns"]:
                m = re.search(pat, text, re.IGNORECASE)
                if m:
                    line_no = text[: m.start()].count("\n") + 1
                    line_text = text.splitlines()[line_no - 1].strip()[:160]
                    evidence[key].append((rel, f"L{line_no}: {line_text}"))
                    break

    return evidence, file_list


def structural_checks(root, file_list):
    names = {p.name.lower() for p in file_list}

    # Gate requirement: "a SUBMISSION.md at its root" — direct child of repo root only.
    submission_at_root = any(
        p.name.lower() == "submission.md" and p.parent == root for p in file_list
    )
    submission_anywhere = any(p.name.lower() == "submission.md" for p in file_list)

    manifest_files = ["requirements.txt", "package.json", "pyproject.toml", "go.mod", "pipfile"]
    has_manifest = any(m in names for m in manifest_files)
    has_entrypoint = any(p.name in ENTRYPOINT_NAMES for p in file_list)

    return {
        "has_submission_md_at_root": submission_at_root,
        "has_submission_md_anywhere": submission_anywhere,
        "has_manifest": has_manifest,
        "has_entrypoint": has_entrypoint,
    }


STUB_MARKER_PATTERN = re.compile(
    r"NotImplementedError|(?:#|//)\s*TODO|(?:#|//)\s*FIXME|"
    r"pass\s*#.*(?:todo|implement)|\.{3}\s*#\s*implement",
    re.IGNORECASE,
)

IGNORED_DIRS = {".git", "node_modules", "venv", ".venv", "__pycache__", "dist", "build"}


def code_health_signals(root, file_list):
    """Static, non-executing signals for the 'It works' criterion. This is NOT
    a substitute for watching the demo — a repo can parse cleanly and still
    fail at runtime (missing env vars, wrong credentials, version mismatches).
    It only catches the strong negative signal of code that isn't even valid,
    or that still contains unfinished stubs."""
    syntax_errors = []
    stub_markers = []
    code_lines = 0

    for path in file_list:
        if any(part in IGNORED_DIRS for part in path.parts):
            continue
        rel = path.relative_to(root).as_posix()

        if path.suffix == ".py":
            try:
                source = path.read_text(errors="ignore")
            except Exception:
                continue
            try:
                ast.parse(source, filename=rel)
            except SyntaxError as e:
                syntax_errors.append(f"{rel}: line {e.lineno}: {e.msg}")
            code_lines += len([ln for ln in source.splitlines() if ln.strip()])

        elif path.suffix in {".js", ".ts", ".jsx", ".tsx"}:
            try:
                source = path.read_text(errors="ignore")
            except Exception:
                continue
            code_lines += len([ln for ln in source.splitlines() if ln.strip()])

        else:
            continue

        for m in STUB_MARKER_PATTERN.finditer(source):
            line_no = source[: m.start()].count("\n") + 1
            stub_markers.append(f"{rel}:{line_no}")

    return {
        "syntax_errors": syntax_errors,
        "stub_markers": stub_markers,
        "code_lines": code_lines,
    }


def git_activity(root):
    log = run(["git", "log", "--oneline"], cwd=root)
    commit_count = len(log.stdout.strip().splitlines()) if log.stdout.strip() else 0
    shortlog = run(["git", "shortlog", "-sn", "--all"], cwd=root)
    contributors = [
        line.split(maxsplit=1)[-1] for line in shortlog.stdout.strip().splitlines()
    ] if shortlog.stdout.strip() else []
    return commit_count, contributors


def part_b_suggested_scores(evidence):
    """Part B is 'verified by AI from your public repo' — full credit if the
    rubric's evidence is present, zero otherwise. Still a starting point:
    the judge can zero out anything that looks like unused/dead code."""
    scores = {}
    for crit in RUBRIC["part_b"]["criteria"]:
        found = bool(evidence.get(crit["evidence_key"]))
        scores[crit["key"]] = crit["max"] if found else 0
    return scores


def analyze_repo(url, dest, log=print):
    """Clone url into dest, scan it, return a result dict. Caller deletes dest."""
    clone_repo(url, dest, log=log)
    evidence, file_list = collect_evidence(dest)
    structural = structural_checks(dest, file_list)
    commit_count, contributors = git_activity(dest)
    return {
        "url": url,
        "evidence": evidence,
        "structural": structural,
        "commit_count": commit_count,
        "contributors": contributors,
        "part_b_suggested": part_b_suggested_scores(evidence),
        "code_health": code_health_signals(dest, file_list),
    }
