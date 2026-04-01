
import streamlit as st
import pandas as pd
import time

from extractor import extract_text_from_uploads
from scorer import score_candidate
from questions import generate_questions

st.set_page_config(page_title="Resume Screening AI", layout="wide")
st.title("Resume Screening AI")

#----Inputs----
col1,col2 = st.columns(2)
with col1:
    job_description = st.text_area("Enter Job Description", height=300)

with col2:
    uploaded_files = st.file_uploader("Upload Resumes (PDF)", accept_multiple_files=True, type=["pdf"]) 
#----Process----

# Show how many files are uploaded
if uploaded_files:
    st.info(f"📁 {len(uploaded_files)} resume(s) uploaded — ready to screen")
    
# ── Button triggers ALL processing ───────────────────────
if st.button("Screen Candidates",key="btn_screen"):

    #Validate inputs first
    if not job_description.strip():
        st.error("❌ Job description cannot be empty")
        st.stop()
    if not uploaded_files:
        st.error("❌ Please upload at least one resume")
        st.stop()

    # ── Extract text from ALL uploaded files ──────────────
    # test_files = uploaded_files
    st.write(f"Extracting text from {len(uploaded_files)} resume(s)...")
    resumes = extract_text_from_uploads(uploaded_files)
    st.write(f"✅ Extracted {len(resumes)} resumes successfully")
    # ── Process each resume one by one ───────────────────
    progress_bar = st.progress(0)
    status_text = st.empty()
    total = len(resumes)
    results = []
    for i, (name,text) in enumerate(resumes.items(), 1):
        status_text.text(f"Processing resume {i}/{total}: {name}")
        progress_bar.progress(i / total)

        try:
            score_data = score_candidate(text, job_description)
            questions = generate_questions(text, job_description)
            results.append({
                "filename": name,
                "resume_text": text,
                "questions": questions,
                **score_data
            })
            st.write(f"✅ {name} — Score: {score_data['overall_score']}/100 | {score_data['recommendation'].upper()}")
        except Exception as e:
            st.warning(f"❌ Failed  processing on  {name}: {e}")

        # Wait between resumes to avoid quota errors

        if i<total:
            time.sleep(3)

    # Sort by score and save to session
    results = sorted(results, key=lambda x: x["overall_score"], reverse=True)
    st.session_state["results"] = results  # ← saved here, persists across reruns
    status_text.text("✅ All resumes processed")

# ── Results — reads from session state ───────────────────
if "results" in st.session_state:
    results = st.session_state["results"]
    st.subheader(f"Ranked Candidates ({len(results)} total)")

    #Summary table 
    df = pd.DataFrame([{
        "Candidate": r["filename"].replace(".pdf",""),
        "Overall Score": r["overall_score"],
        "Experience Fit": r["experience_fit"],
        "Recommendation": r["recommendation"],
        "Missing Skills": ", ".join(r["missing_skills"][:3])
    } for r in results])

    st.dataframe(df, use_container_width=True)
    st.download_button("Export CSV", data=df.to_csv(index=False), file_name="candidate_report.csv", key="btn_export_csv")


    #Per Candidate Detail View
    st.subheader("Candidate Details")
    options = [r["filename"].replace(".pdf", "") for r in results]
    selected_candidate = st.selectbox("Select Candidate", options=options)
    candidate = next(r for r in results if r["filename"].replace(".pdf", "") == selected_candidate)

    c1,c2,c3 = st.columns(3)
    c1.metric("Overall Score", f"{candidate['overall_score']}/100")
    c2.metric("Experience Fit", candidate["experience_fit"].capitalize())
    c3.metric("Recommendation", candidate["recommendation"].capitalize())

    with st.expander("Reasoning"):
        st.write(candidate["reasoning"])
    
    with st.expander("Skills Match"):
        st.write("**Matched:**", ", ".join(candidate["skills_match"]))
        st.write("**Missing:**", ", ".join(candidate["missing_skills"]))

    with st.expander("Interview Questions"):
        for i,q in enumerate(candidate["questions"],1):
            st.markdown(f"**Q{i} [({q['type'].title()})]** {q['question']}")
            st.caption(f"Assesses: {q['what_to_assess']}")