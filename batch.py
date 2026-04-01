#import concurrent.futures
import time
from  scorer import score_candidate
from questions import generate_questions

def process_batch_candidates(resumes: dict[str,str], job_description: str) -> list[dict]:
    """Process multiple resumes in parallel."""
    # Process each resume in parallel using a thread pool
    # max_workers controls the number of threads to use for parallel processing like 4 resumes processed at once

    results = []
    total = len(resumes)

    for i, (name, text) in enumerate(resumes.items(), start=1):
        print(f"Processing resume {i}/{total}: {name}")
        try:
            score_data = score_candidate(text, job_description)  #Gemini  Call 1
            questions = generate_questions(text, job_description)  #Gemini  Call 2
            results.append({
                "filename": name,
                "resume_text": text,
                "questions": questions,
                **score_data
            })
            print(f"[BATCH] ✓ Score: {score_data['overall_score']}")
        except Exception as e:
            print(f"Error processing {name}: {e}")
        
        if i < total:
            time.sleep(3) # wait 3s between resumes — prevents quota errors

    #Sort by score descending
    return sorted(results, key=lambda x: x["overall_score"], reverse=True)





    # def process_single_candidate(name_text: tuple) -> dict:
    #     name, text = name_text
    #     score_data = score_candidate(text, job_description)
    #     questions = generate_questions(text, job_description)
    #     return {
    #         "filename": name,
    #         "resume_text": text,
    #         "questions": questions,
    #         **score_data
    #     }

    # with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
    #     results = list(executor.map(process_single_candidate, resumes.items()))

    # # Sort by score descending
    # return sorted(results, key=lambda x: x["overall_score"], reverse=True)

    

