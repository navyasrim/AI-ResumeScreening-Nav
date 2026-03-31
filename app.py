import streamlit as st
import pandas as pd
from extractor import extract_text_from_uploads
from batch import process_batch_candidates

st.set_page_config(page_title="Resume Screening AI", layout="wide")
st.title("Resume Screening AI")

#----Inputs----
col1,col2 = st.columns(2)
with col1:
    job_description = st.text_area("Enter Job Description", height=300)

with col2:
    uploaded_files = st.file_uploader("Upload Resumes (PDF)", accept_multiple_files=True, type=["pdf"]) 
#----Process----
if st.button("Screen Candidates") and job_description and uploaded_files:
    test_files = uploaded_files[:1]
    with st.spinner(f"Analyzing {len(test_files)} resumes with Gemini..."):
        resumes = extract_text_from_uploads(test_files)
        results = process_batch_candidates(resumes, job_description)
        st.session_state["results"] = results

    #----Display Results----
    if "results" in st.session_state:
        results = st.session_state["results"]
        #Summary table 
        df = pd.DataFrame([{
            "Candidate": r["filename"].replace(".pdf",""),
            "Overall Score": r["overall_score"],
            "Experience Fit": r["experience_fit"],
            "Recommendation": r["recommendation"],
            "Missing Skills": ", ".join(r["missing_skills"][:3])
        } for r in results])

        st.dataframe(df, use_container_width=True)
        st.download_button("Export CSV", data=pd.DataFrame(results).to_csv(index=False), file_name="candidate_report.csv")

        #Per Candidate Detail View
        st.subheader("Candidate Details")
        selected_candidate = st.selectbox("Select Candidate", options=[r["filename"] for r in results])
        candidate = next(r for r in results if r["filename"] == selected_candidate)

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