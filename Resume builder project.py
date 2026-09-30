"""A friendly, beginner-level command-line resume builder.
This project is designed for an introductory programming course. It uses
ordinary Python features instead of external packages, so a student can read
the source, run it, and change it with a standard Python installation.
Run this file with Python 3. The program asks questions and saves a text
resume in the current folder when the user chooses the save option.
Run this file with Python 3. The program asks questions and prints a text
resume preview when requested.
"""
from datetime import date
from pathlib import Path
import random
import re

SECTION_NAMES = (
    "Personal details",
    "Education",
    "Experience",
    "Projects",
    "Skills",
    "Achievements",
)
SECTION_HINTS = {
    "Personal details": "Name, email, phone, city, and a short summary",
    "Education": "Course, institution, graduation year, and result",
    "Experience": "Role, organization, dates, and what you contributed",
    "Projects": "Project name, tools used, and the problem it solves",
    "Skills": "Programming languages, tools, and people skills",
    "Achievements": "Awards, certificates, volunteering, or milestones",
}

TEMPLATES = {
    "1": "Classic",
    "2": "Compact",
}

def print_rule(character="-", width=60):
    print(character * width)

def print_title(title):
    print()
    print_rule("=")
    print(title.center(60))
    print_rule("=")

def pause():
    input("\nPress Enter to continue... ")

def clean_text(value):
    words = value.strip().split()
    return " ".join(words)

def ask_non_empty(prompt, allow_skip=False):
    while True:
        answer = clean_text(input(prompt))
        if answer:
            return answer
        if allow_skip:
            return ""
        print("Please enter something so this field is not blank.")

def ask_yes_no(prompt, default=True):
    hint = "Y/n" if default else "y/N"
    while True:
        answer = input(f"{prompt} ({hint}): ").strip().lower()
        if answer == "":
            return default
        if answer in ("y", "yes"):
            return True
        if answer in ("n", "no"):
            return False
        print("Please type y or n.")

def ask_menu_choice(prompt, valid_choices):
    while True:
        choice = input(prompt).strip()
        if choice in valid_choices:
            return choice
        print("That choice is not in the menu. Please try again.")

def ask_integer(prompt, minimum=None, maximum=None, allow_skip=False):
    while True:
        raw_value = input(prompt).strip()
        if allow_skip and raw_value == "":
            return None
        try:
            number = int(raw_value)
        except ValueError:
            print("Please enter a whole number.")
            continue
        if minimum is not None and number < minimum:
            print(f"Enter a number that is at least {minimum}.")
            continue
        if maximum is not None and number > maximum:
            print(f"Enter a number no greater than {maximum}.")
            continue
        return number

def valid_email(email):
    pattern = r"^[^\s@]+@[^\s@]+\.[^\s@]+$"
    return re.match(pattern, email) is not None
    parts = email.split("@")
    return len(parts) == 2 and "." in parts[1] and " " not in email

def ask_email(prompt):
    while True:
        email = input(prompt).strip()
        if email == "":
            return ""
        if valid_email(email):
            return email
        print("That email does not look right. Try name@example.com.")

def ask_phone(prompt):
    while True:
        phone = input(prompt).strip()
        if phone == "":
            return ""
        digits = [character for character in phone if character.isdigit()]
        allowed = all(character.isdigit() or character in "+-() ." for character in phone)
        if allowed and 7 <= len(digits) <= 15:
            return phone
        print("Use 7 to 15 digits and only ordinary phone symbols.")

def split_items(text):
    parts = text.split(",")
    items = []
    for part in parts:
        item = clean_text(part)
        if item:
            items.append(item)
    return items

def unique_in_order(items):
    result = []
    seen = set()
    for item in items:
        key = item.casefold()
        if key not in seen:
            result.append(item)
            seen.add(key)
    return result

def ask_list(prompt, allow_skip=True, unique=True):
    while True:
        raw_value = input(prompt).strip()
        if raw_value == "" and allow_skip:
            return []
        items = split_items(raw_value)
        if items:
            return unique_in_order(items) if unique else items
        print("Please enter at least one item, separated with commas.")

def ask_multiline_list(label, required=False):
    print(f"\nAdd {label.lower()} one at a time.")
    print("Leave an entry blank when you are finished.")
    entries = []
    while True:
        entry = clean_text(input(f"{label} #{len(entries) + 1}: "))
        if entry == "":
            if required and not entries:
                print(f"Please add at least one {label.lower()} item.")
                continue
            break
        entries.append(entry)
    return unique_in_order(entries)

def make_empty_resume():
    return {
        "personal": {
            "name": "",
            "email": "",
            "phone": "",
            "city": "",
            "summary": "",
        },
        "education": [],
        "experience": [],
        "projects": [],
        "skills": [],
        "achievements": [],
        "template": "Classic",
        "created": date.today().isoformat(),
    }

def collect_personal_details(resume):
    print_title("Personal details")
    personal = resume["personal"]
    personal["name"] = ask_non_empty("Full name: ")
    personal["email"] = ask_email("Email (optional): ")
    personal["phone"] = ask_phone("Phone (optional): ")
    personal["city"] = ask_non_empty("City or location (optional): ", allow_skip=True)
    print("\nWrite two or three honest sentences about your interests and strengths.")
    personal["summary"] = ask_non_empty("Profile summary (optional): ", allow_skip=True)
    return personal

def collect_education(resume):
    print_title("Education")
    if not ask_yes_no("Would you like to add education details?"):
        return resume["education"]
    records = resume["education"]
    while True:
        record = {
            "course": ask_non_empty("Course or qualification: "),
            "institution": ask_non_empty("Institution: "),
            "year": ask_non_empty("Graduation year (or expected year): "),
            "result": ask_non_empty("Result or relevant note (optional): ", allow_skip=True),
        }
        records.append(record)
        if not ask_yes_no("Add another education record?", default=False):
            break
    return records

def collect_experience(resume):
    print_title("Experience")
    print("You can include internships, part-time work, or volunteering.")
    if not ask_yes_no("Would you like to add experience?"):
        return resume["experience"]
    records = resume["experience"]
    while True:
        role = ask_non_empty("Role or position: ")
        organization = ask_non_empty("Organization: ")
        dates = ask_non_empty("Dates (for example, Jun 2025 - Aug 2025): ")
        details = ask_list("Main contributions, separated by commas: ", allow_skip=False)
        records.append({
            "role": role,
            "organization": organization,
            "dates": dates,
            "details": details,
        })
        if not ask_yes_no("Add another experience record?", default=False):
            break
    return records

def collect_projects(resume):
    print_title("Projects")
    if not ask_yes_no("Would you like to add a project?"):
        return resume["projects"]
    projects = resume["projects"]
    while True:
        name = ask_non_empty("Project name: ")
        description = ask_non_empty("What does it do? (one sentence): ")
        tools = ask_list("Tools or languages used (comma-separated): ", allow_skip=True)
        projects.append({"name": name, "description": description, "tools": tools})
        if not ask_yes_no("Add another project?", default=False):
            break
    return projects

def collect_skills(resume):
    print_title("Skills")
    skills = ask_list("Enter skills separated by commas: ", allow_skip=False)
    resume["skills"] = skills
    print(f"Saved {len(skills)} distinct skill(s).")
    return skills

def collect_achievements(resume):
    print_title("Achievements")
    resume["achievements"] = ask_multiline_list("Achievements", required=False)
    return resume["achievements"]

def choose_template(resume):
    print_title("Choose a layout")
    for number, template_name in TEMPLATES.items():
        print(f"{number}. {template_name}")
    choice = ask_menu_choice("Layout number: ", TEMPLATES.keys())
    resume["template"] = TEMPLATES[choice]
    return resume["template"]

def bullet_lines(items, indent="  "):
    lines = []
    for item in items:
        lines.append(f"{indent}* {item}")
    return lines

def add_section(lines, heading, content_lines):
    if not content_lines:
        return
    lines.append("")
    lines.append(heading.upper())
    lines.append("-" * len(heading))
    lines.extend(content_lines)

def format_personal(personal, compact=False):
    lines = [personal["name"].upper()]
    contact = []
    for key in ("email", "phone", "city"):
        if personal[key]:
            contact.append(personal[key])
    if contact:
        separator = " | " if compact else "  •  "
        lines.append(separator.join(contact))
    if personal["summary"]:
        lines.extend(["", "PROFILE", personal["summary"]])
    return lines

def format_education(records):
    lines = []
    for record in records:
        title = f"{record['course']} — {record['institution']}"
        lines.append(title)
        lines.append(f"  {record['year']}")
        if record["result"]:
            lines.append(f"  {record['result']}")
    return lines

def format_experience(records):
    lines = []
    for record in records:
        lines.append(f"{record['role']} — {record['organization']}")
        lines.append(f"  {record['dates']}")
        lines.extend(bullet_lines(record["details"], indent="  "))
    return lines

def format_projects(projects):
    lines = []
    for project in projects:
        lines.append(project["name"])
        lines.append(f"  {project['description']}")
        if project["tools"]:
            lines.append("  Tools: " + ", ".join(project["tools"]))
    return lines

def build_resume_text(resume):
    compact = resume["template"] == "Compact"
    lines = format_personal(resume["personal"], compact=compact)
    add_section(lines, "Education", format_education(resume["education"]))
    add_section(lines, "Experience", format_experience(resume["experience"]))
    add_section(lines, "Projects", format_projects(resume["projects"]))
    if resume["skills"]:
        add_section(lines, "Skills", [", ".join(resume["skills"])])
    add_section(lines, "Achievements", bullet_lines(resume["achievements"]))
    return "\n".join(lines).strip() + "\n"

def display_resume(resume):
    print_title("Resume preview")
    print(build_resume_text(resume))
    print_rule()

def safe_filename(name):
    cleaned = re.sub(r"[^A-Za-z0-9_-]+", "_", name.strip())
    cleaned = cleaned.strip("_")
    return cleaned or "my_resume"

def save_resume(resume):
    default_name = safe_filename(resume["personal"]["name"]) + "_resume.txt"
    print(f"\nSuggested file name: {default_name}")
    file_name = input("File name (press Enter to use suggestion): ").strip()
    if not file_name:
        file_name = default_name
    if not file_name.lower().endswith(".txt"):
        file_name += ".txt"
    try:
        path = Path(file_name)
        path.write_text(build_resume_text(resume), encoding="utf-8")
    except OSError as error:
        print(f"The file could not be saved: {error}")
        return None
    print(f"Resume saved to: {path.resolve()}")
    return path

def count_resume_items(resume):
    counts = {
        "Education": len(resume["education"]),
        "Experience": len(resume["experience"]),
        "Projects": len(resume["projects"]),
        "Skills": len(resume["skills"]),
        "Achievements": len(resume["achievements"]),
    }
    return counts

def show_resume_stats(resume):
    print_title("Resume contents")
    counts = count_resume_items(resume)
    for section, amount in counts.items():
        print(f"{section:14} : {amount}")
    print(f"{'Template':14} : {resume['template']}")

def search_resume(resume):
    print_title("Search your resume")
    query = clean_text(input("Word or phrase to find: "))
    if not query:
        print("No search phrase was entered.")
        return []
    matches = []
    for number, line in enumerate(build_resume_text(resume).splitlines(), start=1):
        if query.casefold() in line.casefold():
            matches.append((number, line))
    if matches:
        print(f"Found {len(matches)} matching line(s):")
        for number, line in matches:
            print(f"{number:>3}: {line}")
    else:
        print("No matching text was found.")
    return matches

def sort_skills(resume):
    sorted_skills = sorted(resume["skills"], key=str.casefold)
    print_title("Skills in alphabetical order")
    if not sorted_skills:
        print("There are no skills to sort yet.")
    else:
        for index, skill in enumerate(sorted_skills, start=1):
            print(f"{index}. {skill}")
    return sorted_skills

def reverse_skills(resume):
    print_title("Skills in reverse entry order")
    reversed_skills = resume["skills"][::-1]
    if not reversed_skills:
        print("There are no skills to reverse yet.")
    else:
        for skill in reversed_skills:
            print(f"- {skill}")
    return reversed_skills

def skill_overlap(resume):
    print_title("Compare skills with a job")
    job_skills = ask_list("Job skills, separated by commas: ", allow_skip=False)
    resume_set = {skill.casefold() for skill in resume["skills"]}
    job_set = {skill.casefold() for skill in job_skills}
    matched = sorted(resume_set & job_set)
    missing = sorted(job_set - resume_set)
    print(f"Matching skills: {', '.join(matched) if matched else 'none yet'}")
    print(f"Skills to consider learning: {', '.join(missing) if missing else 'none'}")
    return matched, missing

def count_words(text):
    words = text.split()
    count = 0
    for word in words:
        if word:
            count += 1
    return count

def summary_word_count(resume):
    summary = resume["personal"]["summary"]
    amount = count_words(summary)
    print_title("Profile summary length")
    print(f"Your summary contains {amount} word(s).")
    if amount == 0:
        print("Add a short summary if you want an introduction at the top.")
    elif amount > 60:
        print("Consider trimming it so the most useful details stand out.")
    else:
        print("This is a readable length for a short introductory profile.")
    return amount

def completeness_score(resume):
    checks = [
        bool(resume["personal"]["name"]),
        bool(resume["personal"]["email"] or resume["personal"]["phone"]),
        bool(resume["education"]),
        bool(resume["skills"]),
        bool(resume["projects"] or resume["experience"]),
    ]
    completed = sum(1 for check in checks if check)
    return completed, len(checks)

def show_checklist(resume):
    print_title("Quick resume checklist")
    checks = [
        ("Name is present", bool(resume["personal"]["name"])),
        ("At least one contact method", bool(resume["personal"]["email"] or resume["personal"]["phone"])),
        ("Education is included", bool(resume["education"])),
        ("Skills are included", bool(resume["skills"])),
        ("Experience or a project is included", bool(resume["experience"] or resume["projects"])),
        ("Summary is included", bool(resume["personal"]["summary"])),
    ]
    for label, completed in checks:
        mark = "[x]" if completed else "[ ]"
        print(f"{mark} {label}")
    score, total = completeness_score(resume)
    print(f"\nCore sections completed: {score} of {total}")

def edit_personal_details(resume):
    old_personal = resume["personal"].copy()
    print("Current name:", old_personal["name"])
    if ask_yes_no("Replace personal details?"):
        collect_personal_details(resume)
    return resume["personal"]

def edit_skills(resume):
    print("Current skills:", ", ".join(resume["skills"]) or "none")
    if ask_yes_no("Replace the complete skills list?"):
        collect_skills(resume)
    return resume["skills"]

def remove_skill(resume):
    print_title("Remove a skill")
    if not resume["skills"]:
        print("There are no skills to remove.")
        return False
    for index, skill in enumerate(resume["skills"], start=1):
        print(f"{index}. {skill}")
    position = ask_integer("Skill number to remove: ", minimum=1, maximum=len(resume["skills"]))
    removed = resume["skills"].pop(position - 1)
    print(f"Removed: {removed}")
    return True

def add_random_prompt():
    prompts = [
        "What problem did your project solve for another person?",
        "Which class assignment taught you a useful technical skill?",
        "When did you explain a difficult idea clearly to someone?",
        "What did you improve after receiving feedback?",
        "Which result can you describe with a number or example?",
    ]
    prompt = random.choice(prompts)
    print_title("A writing prompt")
    print(prompt)
    return prompt

def section_guide():
    print_title("Section guide")
    for section in SECTION_NAMES:
        print(f"\n{section}")
        print(f"  {SECTION_HINTS[section]}")

def show_menu():
    print_title("Resume Builder")
    print("1. Create a new resume")
    print("2. Preview current resume")
    print("3. Save current resume")
    print("3. Display current resume")
    print("4. Check resume sections")
    print("5. Search resume text")
    print("6. Sort skills")
    print("7. Reverse skill order")
    print("8. Compare skills with a job")
    print("9. Edit personal details")
    print("10. Replace skills")
    print("11. Remove a skill")
    print("12. Count summary words")
    print("13. Show a writing prompt")
    print("14. Show section guide")

    print("13. Show section guide")
    print("0. Quit")
    return {str(number) for number in range(15)}
    return {str(number) for number in range(14)}

def create_resume_workflow(resume):
    collect_personal_details(resume)
    collect_education(resume)
    collect_experience(resume)
    collect_projects(resume)
    collect_skills(resume)
    collect_achievements(resume)
    choose_template(resume)
    print("\nYour information has been collected.")
    return resume

def handle_menu_choice(choice, resume):
    if choice == "1":
        create_resume_workflow(resume)
    elif choice == "2":
        display_resume(resume)
    elif choice == "3":
        save_resume(resume)
        display_resume(resume)
    elif choice == "4":
        show_checklist(resume)
    elif choice == "5":
        search_resume(resume)
    elif choice == "6":
        sort_skills(resume)
    elif choice == "7":
        reverse_skills(resume)
    elif choice == "8":
        skill_overlap(resume)
    elif choice == "9":
        edit_personal_details(resume)
    elif choice == "10":
        edit_skills(resume)
    elif choice == "11":
        remove_skill(resume)
    elif choice == "12":
        summary_word_count(resume)
    elif choice == "13":
        add_random_prompt()
    elif choice == "14":
        section_guide()
    elif choice == "0":
        return False
    else:
        print("That option is not available.")
    return True

def run_program():
    resume = make_empty_resume()
    print("Welcome! This program will help you draft a simple resume.")
    print("Use truthful details and review the saved text before sharing it.")
    running = True
    while running:
        valid_choices = show_menu()
        choice = ask_menu_choice("Choose an option: ", valid_choices)
        running = handle_menu_choice(choice, resume)
        if running:
            pause()
    print("\nThanks for using Resume Builder. Good luck with your applications!")

def main():
    try:
        run_program()
    except (KeyboardInterrupt, EOFError):
        print("\nInput ended. Your current unsaved changes are still in memory only.")

if __name__ == "__main__":
    main()