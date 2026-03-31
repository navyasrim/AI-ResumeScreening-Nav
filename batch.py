import concurrent.futures
from  scorer import score_candidate
from questions import generate_questions

def process_batch_candidates(resumes: dict[str,str], job_description: str, max_workers: int = 4) -> list[dict]:
    """Process multiple resumes in parallel."""

    def process_single_candidate(name_text: tuple) -> dict:
        name, text = name_text
        score_data = score_candidate(text, job_description)
        questions = generate_questions(text, job_description)
        return {
            "filename": name,
            "resume_text": text,
            "questions": questions,
            **score_data
        }

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(process_single_candidate, resumes.items()))

    # Sort by score descending
    return sorted(results, key=lambda x: x["overall_score"], reverse=True)

    

