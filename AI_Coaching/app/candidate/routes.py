import json
from pathlib import Path

from flask import Blueprint, current_app, flash, redirect, render_template, request, session, url_for
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models import Interview, Job, Resume
from app.services.ai_service import analyze_resume, evaluate_interview, generate_interview_questions
from app.services.resume_parser import allowed_file, extract_resume_text
from app.utils import current_user, login_required

candidate_bp = Blueprint("candidate", __name__)


@candidate_bp.route("/dashboard")
@login_required
def dashboard():
    user = current_user()
    if user.role == "admin":
        return redirect(url_for("admin.admin_dashboard"))

    latest_resume = Resume.query.filter_by(user_id=user.id).order_by(Resume.uploaded_at.desc()).first()
    interviews = Interview.query.filter_by(user_id=user.id).order_by(Interview.date.desc()).all()
    jobs = Job.query.order_by(Job.created_at.desc()).all()
    return render_template(
        "candidate/dashboard.html",
        user=user,
        latest_resume=latest_resume,
        interviews=interviews,
        jobs=jobs,
    )


@candidate_bp.route("/profile")
@login_required
def profile():
    user = current_user()
    latest_resume = Resume.query.filter_by(user_id=user.id).order_by(Resume.uploaded_at.desc()).first()
    interviews = Interview.query.filter_by(user_id=user.id).order_by(Interview.date.desc()).all()
    return render_template("candidate/profile.html", user=user, latest_resume=latest_resume, interviews=interviews)


@candidate_bp.route("/upload_resume", methods=["GET", "POST"])
@login_required
def upload_resume():
    user = current_user()
    if request.method == "POST":
        file = request.files.get("file")
        if not file or not file.filename:
            flash("Please choose a resume file.", "danger")
            return redirect(url_for("candidate.upload_resume"))

        if not allowed_file(file.filename, current_app.config["ALLOWED_RESUME_EXTENSIONS"]):
            flash("Only PDF and DOCX files are allowed.", "danger")
            return redirect(url_for("candidate.upload_resume"))

        upload_dir = Path(current_app.config["UPLOAD_FOLDER"]) / str(user.id)
        upload_dir.mkdir(parents=True, exist_ok=True)
        filename = secure_filename(file.filename)
        file_path = upload_dir / filename
        file.save(file_path)

        try:
            resume_text = extract_resume_text(file_path)
        except Exception as exc:
            flash(f"Could not extract text from resume: {exc}", "danger")
            return redirect(url_for("candidate.upload_resume"))

        if not resume_text:
            flash("No readable text was found in the resume.", "danger")
            return redirect(url_for("candidate.upload_resume"))

        analysis = analyze_resume(resume_text)
        resume = Resume(user_id=user.id, file_path=str(file_path), text=resume_text, analysis=analysis)
        db.session.add(resume)
        db.session.commit()

        flash("Resume uploaded and analyzed.", "success")
        return redirect(url_for("candidate.dashboard"))

    return render_template("candidate/upload_resume.html", user=user)


@candidate_bp.route("/start_interview", methods=["POST"])
@login_required
def start_interview():
    payload = request.get_json(silent=True) or {}
    role = (payload.get("role") or request.form.get("role", "Python")).strip()
    if role not in {"Frontend", "Python", "Data Analyst"}:
        role = "Python"

    questions = generate_interview_questions(role)
    session["interview_role"] = role
    session["interview_questions"] = questions

    if request.is_json or request.headers.get("Accept") == "application/json":
        return {"questions": questions}

    return render_template("candidate/mock_interview.html", role=role, questions=questions)


@candidate_bp.route("/mock_interview")
@login_required
def mock_interview():
    questions = session.get("interview_questions")
    role = session.get("interview_role", "Python")
    if not questions:
        questions = generate_interview_questions(role)
        session["interview_questions"] = questions
    return render_template("candidate/mock_interview.html", role=role, questions=questions)


@candidate_bp.route("/evaluate_interview", methods=["POST"])
@login_required
def evaluate_interview_route():
    user = current_user()
    payload = request.get_json(silent=True) or {}
    questions = payload.get("questions") or session.get("interview_questions", [])
    role = payload.get("role") or session.get("interview_role", request.form.get("role", "Python"))
    answers = payload.get("answers")
    if answers is None:
        answers = {
            key.replace("answer_", ""): value.strip()
            for key, value in request.form.items()
            if key.startswith("answer_")
        }

    latest_resume = Resume.query.filter_by(user_id=user.id).order_by(Resume.uploaded_at.desc()).first()
    resume_text = latest_resume.text if latest_resume else ""
    result = evaluate_interview(resume_text, questions, answers)

    interview = Interview(
        user_id=user.id,
        role=role,
        score=int(result.get("score", 0)),
        details={"questions": questions, "answers": answers, "evaluation": result},
    )
    db.session.add(interview)
    db.session.commit()

    session.pop("interview_questions", None)
    session.pop("interview_role", None)

    if request.is_json or request.headers.get("Accept") == "application/json":
        return result

    return render_template("candidate/interview_results.html", interview=interview, result=result)


@candidate_bp.app_template_filter("pretty_json")
def pretty_json(value):
    return json.dumps(value, indent=2)
