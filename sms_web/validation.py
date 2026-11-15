COURSE_CODE_PATTERN = r"[A-Z]{2,4}\d{3}"           # 2–4 letters and 3 digits: DB101, PRG101


def validate_course(form):
    """The rules for a course: a code like DB101, a name (at most 100), a teacher (at most 50), and 1–200 seats."""
    data = {
        "course_code": form.get("course_code", "").strip().upper(),
        "course_name": form.get("course_name", "").strip(),
        "teacher": form.get("teacher", "").strip(),
        "max_students": form.get("max_students", "").strip(),
    }
    errors = {}
    if not re.fullmatch(COURSE_CODE_PATTERN, data["course_code"]):
        errors["course_code"] = "The code is 2–4 letters and 3 digits, like DB101."
    for field, label, limit in [("course_name", "Course name", 100), ("teacher", "Teacher", 50)]:
        if not data[field]:
            errors[field] = f"{label} is required."
        elif len(data[field]) > limit:
            errors[field] = f"{label} can be at most {limit} characters."
    try:
        data["max_students"] = int(data["max_students"])          # "25" -> 25, "" or "many" -> ValueError
        if not 1 <= data["max_students"] <= 200:
            errors["max_students"] = "Max students must be between 1 and 200."
    except ValueError:
        errors["max_students"] = "Max students must be a whole number."
    return data, errors