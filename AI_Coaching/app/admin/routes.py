from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.extensions import db
from app.models import Interview, Job, Resume, User
from app.utils import role_required

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/dashboard", methods=["GET", "POST"])
@role_required("admin")
def admin_dashboard():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        if not title or not description:
            flash("Job title and description are required.", "danger")
        else:
            db.session.add(Job(title=title, description=description))
            db.session.commit()
            flash("Job role created.", "success")
        return redirect(url_for("admin.admin_dashboard"))

    min_score = request.args.get("min_score", type=int)
    query = (
        db.session.query(Interview, User)
        .join(User, Interview.user_id == User.id)
        .order_by(Interview.score.desc(), Interview.date.desc())
    )
    if min_score is not None:
        query = query.filter(Interview.score >= min_score)

    performances = query.all()
    resumes = {resume.user_id: resume for resume in Resume.query.all()}
    jobs = Job.query.order_by(Job.created_at.desc()).all()

    return render_template(
        "admin/admin_dashboard.html",
        performances=performances,
        resumes=resumes,
        jobs=jobs,
        min_score=min_score,
    )


@admin_bp.route("/jobs/<int:job_id>/delete", methods=["POST"])
@role_required("admin")
def delete_job(job_id):
    job = Job.query.get_or_404(job_id)
    db.session.delete(job)
    db.session.commit()
    flash("Job role deleted.", "info")
    return redirect(url_for("admin.admin_dashboard"))
