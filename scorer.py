

from time import time

import google.generativeai as genai
import json, os
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()



api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise RuntimeError("GOOGLE_API_KEY is not set. Please add it to a .env file or your environment.")
genai.configure(api_key=api_key)
model = genai.GenerativeModel("models/gemini-2.5-flash-lite")


def score_candidate(resume_text:str, job_description:str)-> dict:
    prompt = f"""Score this candidate 0-100 against the job description.
Return ONLY valid JSON with these exact keys:
- overall_score: int 0-100
- skills_match: list of matching skills
- missing_skills: list of required but absent skills
- experience_fit: "strong" | "moderate" | "weak"
- recommendation: "advance" | "hold" | "reject"
- reasoning: string, 2 sentences max


    Job Description:
    {job_description}

    Resume:
    {resume_text}

    """
    for attempt in range(3):
        try:
            response = model.generate_content(prompt)
            text = response.text.strip().removeprefix("```json").removesuffix("```").strip()
            return json.loads(text)
        except Exception as e:
            if "429" in str(e) and attempt < 2:
                wait = 15 * (attempt + 1)  # 15s, then 30s
                print(f"Rate limited, waiting {wait}s...")
                time.sleep(wait)
            else:
                raise

