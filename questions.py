import json
from scorer import model

def generate_questions(resume_text: str, job_description: str) -> list:
    prompt = f"""Generate 5 targeted interview questions for this candidate.
Mix behavioral, technical, and situational types.
Focus on gaps or areas needing validation.
Return ONLY a JSON array. Each item must have:
- question: string
- type: "behavioral" | "technical" | "situational"
- what_to_assess: string

Resume (first 2000 chars): {resume_text[:2000]}
Role requirements: {job_description[:500]}"""
    
    response = model.generate_content(prompt)
    text = response.text.strip().removeprefix("```json").removesuffix("```").strip()
    return json.loads(text)
