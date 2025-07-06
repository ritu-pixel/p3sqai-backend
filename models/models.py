import fitz  # PyMuPDF
from pdf2image import convert_from_path
import pytesseract
from langdetect import detect
import re
import json
import google.generativeai as genai

from config import LLM_BACKEND, GOOGLE_API_KEY

from transformers import (
    pipeline,
    MarianMTModel,
    MarianTokenizer
)

# PDF Extraction

def extract_json_from_text(text: str) -> dict | None:
    try:
        start = text.find('{')
        end = text.rfind('}') + 1

        if start == -1 or end == -1 or start >= end:
            return None
        json_str = text[start:end]
        json_obj = json.loads(json_str)
        json_obj["error"] = ""
        return json_obj

    except json.JSONDecodeError:
        return None

def extract_text_from_pdf(path: str) -> str:
    doc = fitz.open(path)
    return " ".join([page.get_text() for page in doc])

def ocr_pdf(path: str) -> str:
    pages = convert_from_path(path)
    return " ".join([pytesseract.image_to_string(p) for p in pages])

def is_scanned_pdf(path: str) -> bool:
    doc = fitz.open(path)
    return all(not page.get_text().strip() for page in doc)


# Summarization / Classification lazy-load setup
classifier = None
summarizer = None
gemini_model = None

clause_labels = ["Obligation", "Penalty", "Liability", "Duration", "Payment Clause", "Risky", "Neutral"]

prompt = """
Analyze the following text with respect to indian laws, and generate a summary and classify each clause into one of the following categories: "Obligation", "Penalty", "Liability", "Duration", "Payment Clause", "Risky" and, "Neutral". Return a structured JSON response with each clause and its label where score is confidence ranging from 0 to 1 with one significant digit.
{
    "summary": "",
    "clauses": [
        {
        "clause": "",
        "label": "",
        "score":
        },
    ]
}
"""

def get_summary(text: str, chunk_size: int = 1000) -> str:
    global summarizer
    if summarizer is None and LLM_BACKEND != "gemini":
        summarizer = pipeline("summarization", model="csebuetnlp/mT5_multilingual_XLSum")

    if LLM_BACKEND == "gemini":
        return "Summary generation with Gemini not implemented here."

    chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
    summaries = [summarizer(chunk)[0]['summary_text'] for chunk in chunks]
    return " ".join(summaries)

def classify_clauses(text: str) -> list:
    global classifier, gemini_model

    if LLM_BACKEND == "gemini":
        if gemini_model is None:
            genai.configure(api_key=GOOGLE_API_KEY)
            gemini_model = genai.GenerativeModel('gemini-1.5-flash-latest')
            print("Using Gemini model for classification and summarization")

        response = gemini_model.generate_content(prompt + text)
        extracted = extract_json_from_text(response.text)
        print("Gemini response:", extracted)
        return extracted

    if classifier is None:
        classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

    clauses = re.split(r'(?<=[.;])\s+', text)
    results = []
    for clause in clauses:
        clause = clause.strip()
        if clause:
            result = classifier(clause, clause_labels)
            results.append({
                "clause": clause,
                "label": result['labels'][0],
                "score": result['scores'][0]
            })

    extracted = {
        "summary": get_summary(text),
        "clauses": results
    }
    return extracted


# Translation

def load_translation_model(src: str, tgt: str):
    model_name = f"Helsinki-NLP/opus-mt-{src}-{tgt}"
    tokenizer = MarianTokenizer.from_pretrained(model_name)
    model = MarianMTModel.from_pretrained(model_name)
    return model, tokenizer

def translate(text: str, src: str = "en", tgt: str = "hi") -> str:
    model, tokenizer = load_translation_model(src, tgt)
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
    translated = model.generate(**inputs)
    return tokenizer.decode(translated[0], skip_special_tokens=True)

def detect_language(text: str) -> str:
    try:
        return detect(text)
    except Exception as e:
        print(f"Language detection error: {e}")
        return "unknown"
