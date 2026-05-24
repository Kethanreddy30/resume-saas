from pathlib import Path

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"


def render_profile_pdf(profile: dict) -> bytes:
    try:
        from weasyprint import HTML
    except OSError as exc:
        raise RuntimeError(
            "PDF export requires WeasyPrint system libraries (GTK/Pango). "
            "See https://doc.courtbouillon.org/weasyprint/stable/first_steps.html"
        ) from exc

    template_path = TEMPLATES_DIR / "resume.html"
    html_content = template_path.read_text(encoding="utf-8")

    skills_html = ", ".join(profile.get("skills") or [])
    experience_html = _render_experience(profile.get("experience") or [])
    education_html = _render_education(profile.get("education") or [])

    html_content = (
        html_content.replace("{{ full_name }}", _escape(profile.get("full_name", "")))
        .replace("{{ email }}", _escape(profile.get("email", "")))
        .replace("{{ summary }}", _escape(profile.get("summary") or ""))
        .replace("{{ skills }}", _escape(skills_html))
        .replace("{{ experience }}", experience_html)
        .replace("{{ education }}", education_html)
    )

    return HTML(string=html_content).write_pdf()


def _render_experience(experience: list) -> str:
    if not experience:
        return "<p>No experience listed.</p>"

    items = []
    for entry in experience:
        if not isinstance(entry, dict):
            continue
        company = _escape(entry.get("company", ""))
        role = _escape(entry.get("role", ""))
        duration = _escape(entry.get("duration", ""))
        description = _escape(entry.get("description", ""))
        items.append(
            f"<p><strong>{role}</strong> — {company} ({duration})<br/>{description}</p>"
        )
    return "\n".join(items) or "<p>No experience listed.</p>"


def _render_education(education: list) -> str:
    if not education:
        return "<p>No education listed.</p>"

    items = []
    for entry in education:
        if not isinstance(entry, dict):
            continue
        institution = _escape(entry.get("institution", ""))
        degree = _escape(entry.get("degree", ""))
        year = _escape(entry.get("year", ""))
        items.append(f"<p><strong>{degree}</strong> — {institution} ({year})</p>")
    return "\n".join(items) or "<p>No education listed.</p>"


def _escape(value: str) -> str:
    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )
