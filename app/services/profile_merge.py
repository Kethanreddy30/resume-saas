from typing import Any


def _is_empty(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return not value.strip()
    return False


def _dedupe_skills(skills: list) -> list:
    seen: set[str] = set()
    result: list[str] = []
    for skill in skills:
        if not isinstance(skill, str):
            continue
        normalized = skill.strip()
        if not normalized:
            continue
        key = normalized.lower()
        if key not in seen:
            seen.add(key)
            result.append(normalized)
    return result


def _dedupe_records(records: list, key_fields: tuple[str, str]) -> list:
    seen: set[tuple[str, str]] = set()
    result: list[dict] = []
    for record in records:
        if not isinstance(record, dict):
            continue
        key = tuple(
            str(record.get(field, "")).strip().lower()
            for field in key_fields
        )
        if not any(key):
            continue
        if key not in seen:
            seen.add(key)
            result.append(record)
    return result


def merge_parsed_into_profile(profile: dict, parsed: dict) -> dict:
    """Return Supabase update payload: fill empty scalars, append list fields."""
    update: dict = {}

    if _is_empty(profile.get("full_name")) and parsed.get("full_name"):
        update["full_name"] = parsed["full_name"]

    if _is_empty(profile.get("summary")) and parsed.get("summary"):
        update["summary"] = parsed["summary"]

    existing_skills = profile.get("skills") or []
    parsed_skills = parsed.get("skills") or []
    if parsed_skills:
        merged_skills = _dedupe_skills(list(existing_skills) + list(parsed_skills))
        if merged_skills != existing_skills:
            update["skills"] = merged_skills

    existing_experience = profile.get("experience") or []
    parsed_experience = parsed.get("experience") or []
    if parsed_experience:
        merged_experience = _dedupe_records(
            list(existing_experience) + list(parsed_experience),
            ("company", "role"),
        )
        if merged_experience != existing_experience:
            update["experience"] = merged_experience

    existing_education = profile.get("education") or []
    parsed_education = parsed.get("education") or []
    if parsed_education:
        merged_education = _dedupe_records(
            list(existing_education) + list(parsed_education),
            ("institution", "degree"),
        )
        if merged_education != existing_education:
            update["education"] = merged_education

    return update
