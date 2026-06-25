# ATS Resume Analyzer

A Streamlit-based resume evaluation app that compares a candidate's resume against a job description and returns an ATS-style score, keyword analysis, section detection, and AI-powered improvement suggestions.

## Features

- Upload a resume in PDF or DOCX format
- Paste the target job description directly into the app
- Receive an ATS compatibility score and breakdown
- See matched, missing, and extra keywords
- Check resume section completeness
- Get AI-powered resume improvement guidance via OpenAI GPT-4o

## Requirements

- Python 3.12 or newer
- `streamlit`
- `openai`
- `python-dotenv`
- `plotly`
- `pandas`
- `pdfplumber`
- `python-docx`

## Setup

1. Clone or open the repository.
2. Create a Python environment and activate it.
3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root and add your OpenAI API key:

```bash
OPENAI_API_KEY="your_openai_api_key"
```

## Running the app

Start the Streamlit app with:

```bash
streamlit run app.py
```

Then open the URL shown by Streamlit in your browser.

## How it works

- `app.py` provides the Streamlit UI, file upload controls, job description input, and results dashboard.
- `resume_logic.py` extracts text from uploaded resume files and sends a structured analysis request to OpenAI.
- The analysis returns an ATS score, keyword matching details, section detection data, and optional AI feedback.

## Notes

- The current interface allows PDF and DOCX uploads.
- If you want to evaluate plain text files, the analysis logic supports text extraction from raw bytes.
- AI feedback requires a valid `OPENAI_API_KEY`.

## Project files

- `app.py` — Streamlit frontend and results dashboard
- `resume_logic.py` — resume text extraction and OpenAI analysis pipeline
- `requirements.txt` — Python dependencies
- `pyproject.toml` — project metadata
- `uploads/` — optional upload storage folder
- `README.md` — project documentation

