"""
resume_logic.py
All ATS analysis logic delegated entirely to OpenAI GPT-4o.
No hardcoded keyword lists, regex patterns, or skill taxonomies.
"""

import json
import openai
from io import BytesIO
from dotenv import load_dotenv
import os

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# ── Optional PDF/DOCX parsers ─────────────────────────────────────────────────
try:
    import pdfplumber
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False

try:
    import docx
    DOCX_SUPPORT = True
except ImportError:
    DOCX_SUPPORT = False


# ══════════════════════════════════════════════════════════════════════════════
# 1.  TEXT EXTRACTION  (file I/O only — no logic here)
# ══════════════════════════════════════════════════════════════════════════════

def extract_text_from_file(uploaded_file) -> str:
    """Extract plain text from an uploaded Streamlit file object (PDF/DOCX/TXT)."""
    filename  = uploaded_file.name.lower()
    raw_bytes = uploaded_file.read()

    if filename.endswith(".pdf"):
        if not PDF_SUPPORT:
            raise ImportError("pdfplumber is required. Run: pip install pdfplumber")
        with pdfplumber.open(BytesIO(raw_bytes)) as pdf:
            pages = [page.extract_text() or "" for page in pdf.pages]
        return "\n".join(pages)

    elif filename.endswith(".docx"):
        if not DOCX_SUPPORT:
            raise ImportError("python-docx is required. Run: pip install python-docx")
        document = docx.Document(BytesIO(raw_bytes))
        return "\n".join(p.text for p in document.paragraphs)

    else:
        return raw_bytes.decode("utf-8", errors="ignore")


# ══════════════════════════════════════════════════════════════════════════════
# 2.  SINGLE LLM ANALYSIS CALL
#     Returns the full structured analysis + improvement feedback in one shot.
# ══════════════════════════════════════════════════════════════════════════════

_SYSTEM_PROMPT = """
You are an expert ATS (Applicant Tracking System) consultant and senior career coach.
Your job is to deeply analyse a candidate's resume against a job description and return
a structured JSON analysis — NO commentary outside the JSON block.

You must infer everything from the actual content of the resume and JD.
Do NOT rely on any fixed keyword list, section template, or skill taxonomy.
Discover keywords, sections, skills, and gaps dynamically from what you read.

Return ONLY a single valid JSON object with this exact schema (no markdown fences):

{
  "ats": {
    "ats_score":       <number 0-100, weighted composite>,
    "keyword_score":   <number 0-100>,
    "section_score":   <number 0-100>,
    "skill_gap_score": <number 0-100>,
    "rating":          <"Excellent" | "Good" | "Fair" | "Needs Work">,
    "score_rationale": <1-2 sentence explanation of the composite score>
  },
  "keywords": {
    "matched":  [<keywords present in both resume and JD>],
    "missing":  [<important JD keywords absent from resume>],
    "extra":    [<resume keywords not in JD — could be bonus or noise>],
    "match_score": <number 0-100>
  },
  "sections": {
    "found":         [<section names detected in the resume>],
    "missing":       [<standard sections absent from the resume>],
    "section_score": <number 0-100>,
    "details":       { "<section name>": <true|false>, ... }
  },
  "skill_gaps": {
    "<Category inferred from JD>": {
      "required_by_jd":    [<skills the JD demands in this category>],
      "present_in_resume": [<of those, skills the resume demonstrates>],
      "gaps":              [<skills required but missing>]
    },
    "gap_score": <number 0-100, higher = fewer gaps>
  },
  "llm_feedback": "<full markdown improvement plan — see instructions below>"
}

For llm_feedback, write a structured improvement plan with these sections:
1. **Executive Summary** – 2-3 sentences on the resume's current ATS standing.
2. **Critical Fixes** – bullet list of max 5 must-do changes before applying.
3. **Keyword Optimisation** – specific keywords to add and exactly where (summary / experience / skills).
4. **Section Improvements** – targeted advice for each missing or weak section.
5. **Skill Gap Remediation** – per gap category: how to address it (surface existing experience, take a course, etc.).
6. **Formatting & ATS Tips** – 3-5 ATS-friendly formatting tips.
7. **Quick Wins** – 3 changes the candidate can make in under 10 minutes.

Address the candidate as "you". Use Markdown. Be specific, actionable, and encouraging.

Scoring weights:
  keyword match   40%
  section score   30%
  skill gap score 30%
"""


def _call_llm(resume_text: str, jd_text: str) -> dict:
    """Single GPT-4o call that returns the full parsed analysis dict."""
    client = openai.OpenAI()

    user_msg = f"""
## Resume
{resume_text[:4000]}

## Job Description
{jd_text[:3000]}

Analyse the resume against the job description and return the JSON object as specified.
"""

    response = client.chat.completions.create(
        model="gpt-4o",
        max_tokens=3000,
        temperature=0.2,          # low temp → consistent, structured output
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user",   "content": user_msg},
        ],
    )

    raw = response.choices[0].message.content
    return json.loads(raw)


# ══════════════════════════════════════════════════════════════════════════════
# 3.  RESULT NORMALISATION
#     Guarantees every key app.py expects is present, even if LLM omits one.
# ══════════════════════════════════════════════════════════════════════════════

def _normalise(data: dict) -> dict:
    """Fill in any missing keys with safe defaults so app.py never KeyErrors."""

    # -- ats block
    ats = data.get("ats", {})
    ats.setdefault("ats_score",       0)
    ats.setdefault("keyword_score",   0)
    ats.setdefault("section_score",   0)
    ats.setdefault("skill_gap_score", 0)
    ats.setdefault("rating",          "Needs Work")
    ats.setdefault("score_rationale", "")
    data["ats"] = ats

    # -- keywords block
    kw = data.get("keywords", {})
    kw.setdefault("matched",     [])
    kw.setdefault("missing",     [])
    kw.setdefault("extra",       [])
    kw.setdefault("match_score", ats.get("keyword_score", 0))
    data["keywords"] = kw

    # -- sections block
    sec = data.get("sections", {})
    sec.setdefault("found",         [])
    sec.setdefault("missing",       [])
    sec.setdefault("section_score", ats.get("section_score", 0))
    sec.setdefault("details",       {})
    data["sections"] = sec

    # -- skill_gaps block
    sg = data.get("skill_gaps", {})
    sg.setdefault("gap_score", ats.get("skill_gap_score", 0))
    data["skill_gaps"] = sg

    # -- feedback
    data.setdefault("llm_feedback", None)

    return data


# ══════════════════════════════════════════════════════════════════════════════
# 4.  MASTER PIPELINE  (single entry point for app.py)
# ══════════════════════════════════════════════════════════════════════════════

def run_ats_analysis(resume_file, jd_text: str, generate_feedback: bool = True) -> dict:
    """
    Full ATS pipeline — everything delegated to GPT-4o.

    Parameters
    ----------
    resume_file      : Streamlit UploadedFile object
    jd_text          : Job description as plain string
    generate_feedback: Included for API compatibility; feedback is always
                       generated as part of the single LLM call when True.

    Returns
    -------
    dict with keys: resume_text, ats, keywords, sections, skill_gaps, llm_feedback
    """
    # Step 1 – extract raw text (file I/O only)
    resume_text = extract_text_from_file(resume_file)

    # Step 2 – single LLM call does ALL analysis + feedback
    raw_result = _call_llm(resume_text, jd_text)

    # Step 3 – normalise to guarantee all keys exist
    result = _normalise(raw_result)

    # Step 4 – suppress feedback if caller opted out
    if not generate_feedback:
        result["llm_feedback"] = None

    # Step 5 – attach raw resume text for any downstream use
    result["resume_text"] = resume_text

    return result