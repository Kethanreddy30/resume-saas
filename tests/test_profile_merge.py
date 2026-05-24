import pytest

from app.services.profile_merge import merge_parsed_into_profile


def test_fill_empty_scalars_only():
    profile = {
        "full_name": "",
        "email": "existing@example.com",
        "summary": "Existing summary",
        "skills": [],
        "experience": [],
        "education": [],
    }
    parsed = {
        "full_name": "Jane Doe",
        "email": "jane@example.com",
        "summary": "New summary",
        "skills": ["Python"],
    }

    result = merge_parsed_into_profile(profile, parsed)

    assert result["full_name"] == "Jane Doe"
    assert "email" not in result
    assert "summary" not in result


def test_append_skills_deduped():
    profile = {
        "full_name": "Jane",
        "summary": "Summary",
        "skills": ["Python", "FastAPI"],
        "experience": [],
        "education": [],
    }
    parsed = {"skills": ["fastapi", "Docker", "Python"]}

    result = merge_parsed_into_profile(profile, parsed)

    assert result["skills"] == ["Python", "FastAPI", "Docker"]


def test_append_experience_deduped_by_company_role():
    profile = {
        "full_name": "Jane",
        "summary": "Summary",
        "skills": [],
        "experience": [
            {"company": "Acme", "role": "Engineer", "duration": "2020-2022"}
        ],
        "education": [],
    }
    parsed = {
        "experience": [
            {"company": "Acme", "role": "Engineer", "duration": "2020-2022"},
            {"company": "Beta", "role": "Senior Engineer", "duration": "2022-2024"},
        ]
    }

    result = merge_parsed_into_profile(profile, parsed)

    assert len(result["experience"]) == 2
    assert result["experience"][1]["company"] == "Beta"


def test_append_education_deduped():
    profile = {
        "full_name": "Jane",
        "summary": "Summary",
        "skills": [],
        "experience": [],
        "education": [{"institution": "MIT", "degree": "BS CS", "year": "2020"}],
    }
    parsed = {
        "education": [
            {"institution": "MIT", "degree": "BS CS", "year": "2020"},
            {"institution": "Stanford", "degree": "MS CS", "year": "2022"},
        ]
    }

    result = merge_parsed_into_profile(profile, parsed)

    assert len(result["education"]) == 2
    assert result["education"][1]["institution"] == "Stanford"


def test_no_changes_returns_empty_update():
    profile = {
        "full_name": "Jane Doe",
        "summary": "Done",
        "skills": ["Python"],
        "experience": [],
        "education": [],
    }
    parsed = {"full_name": "Other", "skills": ["python"]}

    result = merge_parsed_into_profile(profile, parsed)

    assert result == {}
