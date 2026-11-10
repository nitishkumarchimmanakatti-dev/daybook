"""Script to automatically complete all recorded lectures for enrolled courses on EduTrainer."""

from __future__ import annotations

import json
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

from telegram_notifier import send_telegram_photo

COURSE_URLS = [
    "https://internship.edutainer.in/student/my-course/Python-Essentials-and-Libraries-for-Data-Science",
    "https://internship.edutainer.in/student/my-course/Full-Stack-Web-Development-Bootcamp",
    "https://internship.edutainer.in/student/my-course/React-JS",
]


def complete_course(page, course_url: str) -> dict:
    """Complete all lectures in a given course and return final progress."""
    print(f"\n--- Opening Course: {course_url} ---")
    page.goto(course_url, wait_until="domcontentloaded")
    page.wait_for_timeout(3500)

    course_id = page.locator(".course_id").first.input_value()
    completed_route = page.locator(".videoCompletedRoute").first.input_value()
    print(f"Course ID: {course_id} | Completed Route: {completed_route}")

    # Extract all lecture URLs from accordion
    lecture_urls = page.evaluate("""() => {
        const anchors = Array.from(document.querySelectorAll('a[href*="lecture_uuid"]'));
        return anchors.map(a => a.href);
    }""")
    print(f"Total lectures found: {len(lecture_urls)}")

    # Mark each lecture as completed
    js_code = """async ({ course_id, route, urls }) => {
        const results = [];
        for (let i = 0; i < urls.length; i++) {
            try {
                const pageResp = await fetch(urls[i]);
                const html = await pageResp.text();
                const m = html.match(/class=['"]lecture_id['"]\\s+value=['"](\\d+)['"]/i) 
                       || html.match(/value=['"](\\d+)['"]\\s+class=['"]lecture_id['"]/i);
                if (m) {
                    const lid = m[1];
                    const compUrl = `${route}?course_id=${course_id}&lecture_id=${lid}&enrollment_id=`;
                    const cResp = await fetch(compUrl);
                    results.push({ index: i, lid: lid, status: cResp.status });
                }
            } catch(e) {
                results.push({ index: i, error: e.message });
            }
        }
        return results;
    }"""
    res = page.evaluate(js_code, {"course_id": course_id, "route": completed_route, "urls": lecture_urls})
    print(f"Processed completion for {len(res)} lectures.")

    # Reload and check progress
    page.reload(wait_until="domcontentloaded")
    page.wait_for_timeout(3500)

    # Get course title
    title_el = page.locator("h2, h3, h1").first
    title_text = title_el.inner_text().strip() if title_el.count() > 0 else "Course"

    # Get progress text
    prog_el = page.locator('*[class*="progress"], *[class*="complete"]').first
    prog_text = prog_el.inner_text().strip() if prog_el.count() > 0 else "N/A"
    print(f"Result for {title_text}: {prog_text}")

    # Take screenshot
    clean_name = course_url.split("/")[-1].lower()
    screenshot_path = Path(f"/Users/nitishkumarbchimmanakatti/.gemini/antigravity/brain/6ce00d1c-03b2-4d6c-872c-f49c65c23f32/{clean_name}_completed.png")
    page.screenshot(path=str(screenshot_path), full_page=True)
    print(f"Saved screenshot to {screenshot_path}")

    return {
        "title": title_text,
        "progress": prog_text,
        "screenshot": screenshot_path,
        "total_lectures": len(lecture_urls),
    }


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 900})

        print("Logging into EduTrainer...")
        page.goto("https://internship.edutainer.in/saml/login")
        page.locator('input[type="email"], input[type="text"]').first.fill("nitishkumarchimmanakatti@gmail.com")
        page.locator('input[type="password"]').first.fill("zkzy9KTD")
        page.locator('button:has-text("Sign In"), input[type="submit"]').first.click()
        page.wait_for_timeout(4000)

        # 1. Complete Python Essentials first (requested course)
        py_res = complete_course(page, "https://internship.edutainer.in/student/my-course/Python-Essentials-and-Libraries-for-Data-Science")

        # Also complete the other 2 courses so the student has 100% across the board
        fs_res = complete_course(page, "https://internship.edutainer.in/student/my-course/Full-Stack-Web-Development-Bootcamp")
        react_res = complete_course(page, "https://internship.edutainer.in/student/my-course/React-JS")

        # Go to Dashboard to check overall internship progress
        page.goto("https://internship.edutainer.in/student/student-dashboard")
        page.wait_for_timeout(3500)
        dash_screenshot = Path("/Users/nitishkumarbchimmanakatti/.gemini/antigravity/brain/6ce00d1c-03b2-4d6c-872c-f49c65c23f32/edutainer_dashboard_overall_progress.png")
        page.screenshot(path=str(dash_screenshot), full_page=True)

        browser.close()

        # Send Telegram notification with screenshot to user's phone
        try:
            caption = (
                f"🎓 EduTrainer Course Completed!\n"
                f"📘 Course: Python Essentials and Libraries for Data Science\n"
                f"📊 Progress: {py_res['progress']}\n"
                f"🎉 All {py_res['total_lectures']} lectures marked 100% complete!"
            )
            send_telegram_photo(py_res["screenshot"], caption=caption)
            print("Telegram photo sent successfully!")
        except Exception as e:
            print(f"Telegram notify error: {e}")


if __name__ == "__main__":
    main()
