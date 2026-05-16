import json
import os
import re

from groq import Groq


COMMON_SKILLS = [
    "python", "flask", "django", "javascript", "react", "html", "css", "sql",
    "excel", "power bi", "tableau", "pandas", "numpy", "git", "rest api",
    "machine learning", "data analysis", "communication", "leadership"
]

ROLE_SKILLS = {
    "Frontend": ["html", "css", "javascript", "react", "accessibility", "api integration"],
    "Python": ["python", "flask", "sql", "rest api", "testing", "git"],
    "Data Analyst": ["sql", "excel", "power bi", "tableau", "pandas", "statistics"],
}


def _client():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return None
    try:
        return Groq(api_key=api_key)
    except Exception:
        return None


def _ask_groq(prompt, expect_json=True):
    client = _client()
    if not client:
        return None

    try:
        system = "You are an expert career coach. Return concise, structured JSON when requested."
        response = client.chat.completions.create(
            model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            temperature=0.35,
        )
        content = response.choices[0].message.content
        return _json_from_text(content) if expect_json else content
    except Exception:
        return None


def _json_from_text(text):
    """Parse JSON even when the model wraps it in prose or fences."""
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        raise


def _normalize_resume_analysis(analysis):
    """Keep Groq output predictable for templates and database JSON."""
    if not isinstance(analysis, dict):
        analysis = {}

    skills = analysis.get("skills") or []
    if isinstance(skills, str):
        skills = [skill.strip() for skill in skills.split(",") if skill.strip()]

    technologies = analysis.get("key_technologies") or []
    if isinstance(technologies, str):
        technologies = [item.strip() for item in technologies.split(",") if item.strip()]

    match_percentages = analysis.get("match_percentages") or {}
    if isinstance(match_percentages, list):
        converted = {}
        for item in match_percentages:
            if isinstance(item, dict):
                role = item.get("role") or item.get("category") or item.get("job_category")
                percent = item.get("percentage") or item.get("match_percentage") or item.get("score")
                if role:
                    converted[str(role)] = percent or 0
        match_percentages = converted
    if not isinstance(match_percentages, dict):
        match_percentages = {}

    weak_skill_areas = analysis.get("weak_skill_areas") or {}
    if isinstance(weak_skill_areas, list):
        weak_skill_areas = {"General": weak_skill_areas}
    if isinstance(weak_skill_areas, str):
        weak_skill_areas = {"General": [item.strip() for item in weak_skill_areas.split(",") if item.strip()]}
    if not isinstance(weak_skill_areas, dict):
        weak_skill_areas = {}

    return {
        "skills": skills,
        "experience_years": analysis.get("experience_years", "Not detected"),
        "key_technologies": technologies,
        "weak_skill_areas": weak_skill_areas,
        "match_percentages": match_percentages,
    }


def analyze_resume(resume_text, jobs=None):
    prompt = f"""
Given this resume text, extract skills, experience years, and key technologies.
Also identify weak skill areas and match percentage with these job categories:
Frontend, Python, Data Analyst.

Return JSON with keys:
skills, experience_years, key_technologies, weak_skill_areas, match_percentages.

Resume:
{resume_text[:9000]}
"""
    ai_result = _ask_groq(prompt)
    if ai_result:
        return _normalize_resume_analysis(ai_result)

    lower_text = resume_text.lower()
    skills = sorted({skill.title() for skill in COMMON_SKILLS if skill in lower_text})
    match_percentages = {}
    weak_skill_areas = {}

    for role, required in ROLE_SKILLS.items():
        present = [skill for skill in required if skill in lower_text]
        missing = [skill.title() for skill in required if skill not in lower_text]
        match_percentages[role] = round((len(present) / len(required)) * 100)
        weak_skill_areas[role] = missing

    return _normalize_resume_analysis({
        "skills": skills or ["Communication", "Problem Solving"],
        "experience_years": "Not detected",
        "key_technologies": skills[:8],
        "weak_skill_areas": weak_skill_areas,
        "match_percentages": match_percentages,
    })


def generate_interview_questions(role):
    prompt = f"""
Generate a set of 10 interview questions tailored to a candidate who wants to be a {role}.
Tag each with difficulty.
Return JSON with key questions, where each item has question and difficulty.
"""
    ai_result = _ask_groq(prompt)
    if ai_result and ai_result.get("questions"):
        return ai_result["questions"]

    fallback = [
        ("Tell me about a project you are proud of and your role in it.", "Easy"),
        (f"What core skills make someone successful in a {role} role?", "Easy"),
        ("Describe a technical problem you debugged recently.", "Medium"),
        ("How do you prioritize tasks when deadlines conflict?", "Medium"),
        (f"Explain a tool or framework commonly used by a {role}.", "Medium"),
        ("How would you communicate a blocker to a non-technical stakeholder?", "Medium"),
        ("Describe how you validate that your work is correct.", "Medium"),
        (f"What is one advanced {role} concept you are currently improving?", "Hard"),
        ("Walk through how you would approach a new unfamiliar problem.", "Hard"),
        ("Why should a recruiter move you to the next interview round?", "Easy"),
    ]
    return [{"question": question, "difficulty": difficulty} for question, difficulty in fallback]


def evaluate_interview(resume_text, questions, answers):
    qa_pairs = [
        {"question": question.get("question", ""), "answer": answers.get(str(index), "")}
        for index, question in enumerate(questions)
    ]
    prompt = f"""
Evaluate these answers and the resume, give a numeric score out of 100, strengths,
weaknesses, improvement tips, and a study plan.

Return JSON with keys:
score, strengths, weaknesses, improvement_tips, study_plan, recommended_skill_gaps.

Resume:
{resume_text[:8000]}

Questions and answers:
{json.dumps(qa_pairs, indent=2)}
"""
    ai_result = _ask_groq(prompt)
    if ai_result:
        ai_result["score"] = int(ai_result.get("score", 0))
        return ai_result

    answered = sum(1 for answer in answers.values() if answer.strip())
    score = min(100, 45 + answered * 5)
    return {
        "score": score,
        "strengths": ["Clear career intent", "Completed the mock interview"],
        "weaknesses": ["Add more specific metrics and examples", "Practice structured STAR answers"],
        "improvement_tips": [
            "Answer each question with situation, task, action, and result.",
            "Tie examples back to the target role.",
            "Add measurable outcomes where possible.",
        ],
        "study_plan": [
            "Week 1: Revise fundamentals for your chosen role.",
            "Week 2: Build one portfolio project and document decisions.",
            "Week 3: Practice 20 behavioral answers out loud.",
        ],
        "recommended_skill_gaps": ["Role-specific depth", "Interview storytelling", "Measurable project impact"],
    }
