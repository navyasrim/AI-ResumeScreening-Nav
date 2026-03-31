import os
import json
import google.generative  as genai
import fitz

genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
model = genai.GenerativeModel("gemini-2.0-flash")

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(stream=pdf_path.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def safe_json_parse(json_string):
    try:
        return json.loads(json_string)
    except:
        start = json_string.find("{")
        end = json_string.rfind("}") + 1
        return  json.loads(json_string[start:end])
    
