import json
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

ARTIFACT_DIR = Path("/Users/nitishkumarbchimmanakatti/.gemini/antigravity/brain/6ce00d1c-03b2-4d6c-872c-f49c65c23f32")
OUT_MD = ARTIFACT_DIR / "VTU_Online_Assignments_Full_Review.md"
OUT_JSON = ARTIFACT_DIR / "VTU_Online_Assignments_Full_Review.json"

COURSES = [
    {
        "slug": "1-wastewater-treatment-and-recycling",
        "title": "Wastewater Treatment And Recycling",
        "exams": [
            {"id": 270, "name": "Assignments 1"},
            {"id": 271, "name": "Assignments 2"}
        ]
    },
    {
        "slug": "1-privacy-and-security-in-online-social-media",
        "title": "Privacy And Security in online Social Media",
        "exams": [
            {"id": 224, "name": "Assignment 1"},
            {"id": 225, "name": "Assignment 2"}
        ]
    }
]

with sync_playwright() as p:
    email = os.getenv("VTU_ONLINE_EMAIL") or os.getenv("VTU_EMAIL")
    password = os.getenv("VTU_ONLINE_PASSWORD") or os.getenv("VTU_PASSWORD")
    if not email or not password:
        print("[ERROR] VTU credentials not found! Set VTU_ONLINE_EMAIL and VTU_ONLINE_PASSWORD in .env.")
        exit(1)

    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("https://online.vtu.ac.in/auth/login")
    page.wait_for_selector('input[name="email"]')
    page.locator('input[name="email"]').fill(email)
    page.locator('input[name="password"]').fill(password)
    page.locator('button:has-text("Sign in")').click()
    page.wait_for_url("**/dashboard", timeout=15000)

    all_data = {}

    for c in COURSES:
        slug = c["slug"]
        c_title = c["title"]
        all_data[c_title] = []

        for ex in c["exams"]:
            ex_id = ex["id"]
            ex_name = ex["name"]
            res = page.evaluate("""async ({ slug, exId }) => {
                const resp = await fetch('/api/v1/student/my-courses/' + slug + '/exams/' + exId + '/result');
                return await resp.json();
            }""", {"slug": slug, "exId": ex_id})

            data = res.get("data", {})
            att = data.get("attempt_info", {})
            review = data.get("review", [])

            all_data[c_title].append({
                "exam_id": ex_id,
                "exam_name": ex_name,
                "attempt_info": att,
                "review": review
            })

    # Save JSON
    with open(OUT_JSON, "w") as f:
        json.dump(all_data, f, indent=2)

    # Build Markdown
    md_lines = [
        "# VTU Online LMS — Complete Assignments & Quiz Submissions",
        f"**Portal**: https://online.vtu.ac.in  ",
        f"**Student**: `{email}`  ",
        f"**Generated**: {time.strftime('%Y-%m-%d %H:%M:%S')}  \n",
        "---",
        "## Important Context on Assignment Format",
        "On the VTU Online platform, the instructors created the course assignments as **online multiple-choice assessments** (each having 25 questions, 60 minutes) rather than file-upload dropboxes. They are submitted directly through the portal's exam interface under the **'Quiz'** tab of each course player.",
        "Below is the complete record of every question, submitted answer, and official key for all assignments across both courses.\n",
        "---"
    ]

    for c_title, exams in all_data.items():
        md_lines.append(f"\n# {c_title}\n")
        for ex in exams:
            att = ex["attempt_info"]
            md_lines.append(f"## {ex['exam_name']} (Exam ID: {ex['exam_id']})")
            md_lines.append(f"- **Status**: {'Passed ✅' if att.get('is_passed') else 'Submitted'}")
            md_lines.append(f"- **Score**: {att.get('total_correct', 'N/A')} / {att.get('total_questions', '25')} ({att.get('percentage', 'N/A')})\n")
            md_lines.append("| # | Question | Submitted Answer | Correct Answer | Status |")
            md_lines.append("|---|---|---|---|---|")

            for i, q in enumerate(ex["review"], 1):
                q_txt = q.get("question", "").replace("|", "\\|").replace("\n", " ")
                u_ans = q.get("user_answer", "").replace("|", "\\|").replace("\n", " ")
                c_ans = q.get("correct_answer", "").replace("|", "\\|").replace("\n", " ")
                status = "✅ Correct" if q.get("is_correct") else "❌ Incorrect"
                md_lines.append(f"| {i} | {q_txt} | {u_ans} | {c_ans} | {status} |")
            md_lines.append("\n---\n")

    with open(OUT_MD, "w") as f:
        f.write("\n".join(md_lines))

    # Also copy to daybook project dir
    daybook_md = Path("/Users/nitishkumarbchimmanakatti/Projects/daybook/VTU_Online_Assignments_Full_Review.md")
    daybook_md.write_text("\n".join(md_lines))

    print(f"Exported full assignments to {OUT_MD} and {daybook_md}")

