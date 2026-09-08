"""
Judge Voting page — send this page's URL to each judge.

Part A only (judged live, per the guide): It works / Innovation / Business
value / Demo. Votes are appended to a local JSON file (votes_data.json) that
the main dashboard reads to show live averages. Send a judge a link with
their name baked in, e.g. http://<your-laptop-ip>:8501/Judge_Voting?judge=Camila
so they don't have to retype it each time.
"""
import streamlit as st

import voting_store as vs

st.set_page_config(page_title="Ask the Airport — Judge Voting", layout="centered")

st.title("🗳️ Judge Voting")
st.caption("Ask the Airport · Part A — judged live, one vote per team")

data = vs.load_data()
teams = data.get("teams", [])

if not teams:
    st.warning("The organizers haven't configured the team list yet. Check back shortly.")
    st.stop()

query_judge = st.query_params.get("judge", "")
judge_name = st.text_input("Your name", value=query_judge, placeholder="e.g. Camila Dias")

if not judge_name.strip():
    st.info("Enter your name to start voting.")
    st.stop()

judge_name = judge_name.strip()

team = st.selectbox("Team presenting now", teams)

existing = vs.get_vote(team, judge_name)
if existing:
    st.caption(f"You've already voted for **{team}** — submitting again will replace the vote.")

st.divider()

scores = {}
for crit in vs.CRITERIA:
    default = existing["scores"].get(crit["key"], 0) if existing else 0
    scores[crit["key"]] = st.slider(
        f"{crit['label']} (max {crit['max']})",
        min_value=0,
        max_value=crit["max"],
        value=default,
        key=f"slider_{team}_{crit['key']}",
    )
    if crit["key"] == "works":
        st.caption("Works and does what it promises.")
    elif crit["key"] == "innovation":
        st.caption("An angle we haven't seen four times today.")
    elif crit["key"] == "business_value":
        st.caption("Who has this problem, and is this a real answer for them?")
    elif crit["key"] == "demo":
        st.caption("Two minutes, one clear story.")

total = sum(scores.values())
st.metric("Your total for this team", f"{total} / {vs.MAX_TOTAL}")

if st.button("Submit vote", type="primary", use_container_width=True):
    vs.submit_vote(team, judge_name, scores)
    st.success(f"Vote saved for {team}.")

st.divider()

mine = vs.my_votes(judge_name)
if mine:
    st.caption("Your votes so far")
    for t, tot in mine.items():
        st.write(f"**{t}** — {tot} / {vs.MAX_TOTAL}")
