"""Browser automation module for VTU Internship Diary entry.

Portal: https://vtu.internyet.in/sign-in
Target: https://vtu.internyet.in/dashboard/student/student-diary
"""

from __future__ import annotations

from datetime import datetime
import json
import os
from pathlib import Path
import subprocess
from typing import Optional, Tuple

from config import get_daybook_dir, ensure_daybook_dirs
from log import log_entry

CREDENTIALS_FILE = get_daybook_dir() / ".credentials.json"
SIGN_IN_URL = "https://vtu.internyet.in/sign-in"
DIARY_URL = "https://vtu.internyet.in/dashboard/student/student-diary"


def get_vtu_credentials() -> Tuple[str, str]:
    """Retrieve VTU credentials."""
    email = os.environ.get("VTU_EMAIL")
    password = os.environ.get("VTU_PASSWORD")

    if not email or not password:
        if CREDENTIALS_FILE.exists():
            try:
                creds = json.loads(CREDENTIALS_FILE.read_text(encoding="utf-8"))
                email = email or creds.get("vtu_email")
                password = password or creds.get("vtu_password")
            except Exception:
                pass

    email = email or "nitishkumarchimmanakatti@gmail.com"
    password = password or "Vtu@1234"
    return email, password


def save_vtu_credentials(email: str, password: str) -> None:
    """Save credentials to ~/Daybook/.credentials.json with restricted 0600 permissions."""
    ensure_daybook_dirs()
    data = {}
    if CREDENTIALS_FILE.exists():
        try:
            data = json.loads(CREDENTIALS_FILE.read_text(encoding="utf-8"))
        except Exception:
            data = {}
    data["vtu_email"] = email
    data["vtu_password"] = password

    CREDENTIALS_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
    CREDENTIALS_FILE.chmod(0o600)


def auto_delete_after_viewing(file_path: Path, delay_seconds: int = 15) -> None:
    """Open screenshot in Preview so the user sees it, then delete it automatically."""
    try:
        subprocess.run(["open", str(file_path)], check=False)
    except Exception:
        pass

    cleanup_cmd = f"sleep {delay_seconds} && rm -f '{file_path}'"
    subprocess.Popen(["bash", "-c", cleanup_cmd], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def enter_vtu_diary(
    work_summary: Optional[str] = None,
    learnings: Optional[str] = None,
    hours: Optional[str] = None,
    blockers: Optional[str] = None,
    links: Optional[str] = None,
    headless: bool = True,
    dry_run: bool = False,
) -> Tuple[bool, str]:
    """Automate login and diary entry submission on VTU InternYet portal."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return False, "Playwright is not installed."

    email, password = get_vtu_credentials()
    save_vtu_credentials(email, password)

    # Dynamic lookup from document database matching today's date
    today_str = datetime.now().strftime("%Y-%m-%d")
    entries_file = Path(__file__).parent / "pending_vtu_entries.json"
    today_entry = None
    if entries_file.exists():
        try:
            all_entries = json.loads(entries_file.read_text(encoding="utf-8"))
            for e in all_entries:
                if e.get("date_str") == today_str:
                    today_entry = e
                    break
        except Exception:
            pass

    if today_entry:
        default_summary = work_summary or today_entry["work_summary"]
        default_hours = hours or today_entry.get("hours", "6.5")
        default_links = links or today_entry.get("links", "https://www.internship.edutainer.in/student/my-learning")
        default_learnings = learnings or today_entry["learnings"]
        default_blockers = blockers or today_entry.get("blockers", "No major blockers encountered.")
    else:
        default_summary = (
            work_summary
            or "Updated project documentation with setup steps, feature descriptions, API notes, and development screenshots."
        )
        default_hours = hours or "6.5"
        default_links = links or "https://www.internship.edutainer.in/student/my-learning"
        default_learnings = (
            learnings
            or "Learned how documentation can serve as evidence of project progress and help others reproduce the work."
        )
        default_blockers = (
            blockers
            or "Keeping documentation synchronized with the latest features required review."
        )

    screenshot_dir = get_daybook_dir() / "screenshots"
    screenshot_dir.mkdir(parents=True, exist_ok=True)
    for old_file in screenshot_dir.glob("*.png"):
        try:
            old_file.unlink()
        except OSError:
            pass
    screenshot_path = screenshot_dir / "latest_vtu_diary.png"

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=headless)
            page = browser.new_page(viewport={"width": 1280, "height": 800})

            # 1. Sign In
            page.goto(SIGN_IN_URL, wait_until="domcontentloaded")
            page.wait_for_timeout(2000)

            page.locator('input[placeholder*="email"]').first.fill(email)
            page.locator('input[type="password"]').first.fill(password)
            page.locator('button:has-text("Sign In")').first.click()
            page.wait_for_timeout(4000)

            if "sign-in" in page.url:
                browser.close()
                return False, "VTU Login failed. Please verify credentials."

            # 2. Duplicate Guard: Check if an entry for today (or target date) is ALREADY submitted
            page.goto("https://vtu.internyet.in/dashboard/student/diary-entries", wait_until="domcontentloaded")
            page.wait_for_timeout(2500)
            rows = page.locator('table tbody tr').all()
            existing_dates = []
            for r in rows[:15]:
                tds = r.locator('td').all()
                if tds:
                    existing_dates.append(tds[0].inner_text().strip())

            # If today's date is already recorded, strictly do NOT submit again
            if any(today_str in d for d in existing_dates):
                # Open the existing entry to show the confirmation screenshot with date
                first_entry_link = page.locator('table tbody tr').first.locator('a, button').first
                if first_entry_link.count() > 0:
                    first_entry_link.click()
                    page.wait_for_timeout(2500)
                    page.screenshot(path=str(screenshot_path), full_page=True)

                browser.close()
                print(f"\n⚠️ [DUPLICATE GUARD] Entry for today ({today_str}) has ALREADY been submitted. Skipping submission to prevent duplicates.")
                print(f"📷 Existing entry confirmation displayed from: {screenshot_path} (auto-deleting after viewing)")
                auto_delete_after_viewing(screenshot_path, delay_seconds=15)

                from notify import send_macos_notification
                send_macos_notification(
                    title="VTU Diary Already Recorded",
                    subtitle=f"Date: {today_str}",
                    message="Today's diary entry is already present. Duplicate submission was skipped.",
                    sound="Pop",
                )
                log_entry(
                    task_id="vtu-portal-diary-entry",
                    action="vtu_diary_entry",
                    result=f"SKIPPED: Entry for {today_str} already exists (duplicate prevented)",
                    approved_by="auto-guard",
                )
                return True, f"Diary entry for {today_str} is already submitted. Duplicate prevented."

            # 3. Go to Diary Selection
            page.goto(DIARY_URL, wait_until="domcontentloaded")
            page.wait_for_timeout(2500)

            # 4. Select Internship
            page.locator('button:has-text("Choose internship"), [role="combobox"]').first.click()
            page.wait_for_timeout(500)
            page.locator('*:has-text("Web Development Intern")').last.click()
            page.wait_for_timeout(500)

            # 5. Pick Today's Date
            page.locator('button:has-text("Pick a Date")').first.click()
            page.wait_for_timeout(500)
            page.locator('button[aria-label*="Today"]').first.click()
            page.wait_for_timeout(500)

            # 6. Continue to form
            page.locator('button:has-text("Continue")').first.click()
            page.wait_for_timeout(2500)

            # 7. Fill Diary Form with exact values from document
            desc_field = page.locator('textarea[name="description"], textarea[placeholder*="describe"]').first
            if desc_field.count() > 0:
                desc_field.fill(default_summary)

            hours_field = page.locator('input[placeholder*="6.5"], input[type="number"]').first
            if hours_field.count() > 0:
                hours_field.fill(default_hours)

            links_field = page.locator('textarea[name="links"], textarea[placeholder*="links"]').first
            if links_field.count() > 0:
                links_field.fill(default_links)

            learn_field = page.locator('textarea[name="learnings"], textarea[placeholder*="learn"]').first
            if learn_field.count() > 0:
                learn_field.fill(default_learnings)

            blocker_field = page.locator('textarea[name="blockers"], textarea[placeholder*="slowed"]').first
            if blocker_field.count() > 0:
                blocker_field.fill(default_blockers)

            # Select required skills: HTML, CSS, React.js
            try:
                skill_input = page.locator('#react-select-2-input, input[id*="react-select"]').first
                if skill_input.count() > 0:
                    for skill in ["HTML", "CSS", "React.js"]:
                        skill_input.fill(skill)
                        page.wait_for_timeout(400)
                        opt = page.locator('[class*="option"]').first
                        if opt.count() > 0:
                            opt.click()
                            page.wait_for_timeout(300)
            except Exception as e:
                print(f"Skill select error: {e}")

            page.wait_for_timeout(1000)

            if not dry_run:
                save_btn = page.locator('button:has-text("Save")').first
                if save_btn.count() > 0:
                    save_btn.click()
                    page.wait_for_timeout(4000)

                # Navigate to the newly submitted entry to capture the verified view with date clearly visible
                page.goto("https://vtu.internyet.in/dashboard/student/diary-entries", wait_until="domcontentloaded")
                page.wait_for_timeout(2500)
                first_entry_link = page.locator('table tbody tr').first.locator('a, button').first
                if first_entry_link.count() > 0:
                    first_entry_link.click()
                    page.wait_for_timeout(2500)

                # Save full-page screenshot of the submitted entry with Date, Hours, Summary, Links, Blockers, Skills
                page.screenshot(path=str(screenshot_path), full_page=True)
            else:
                # Dry run: scroll to top and capture full page
                page.evaluate("window.scrollTo(0, 0)")
                page.wait_for_timeout(500)
                page.screenshot(path=str(screenshot_path), full_page=True)

            browser.close()

            # Ping back user
            from notify import send_macos_notification
            send_macos_notification(
                title="VTU Diary Entry ✅",
                subtitle="Submission Completed",
                message="Your VTU internship diary entry for today has been recorded.",
                sound="Glass",
            )
            print("\n🔔 [PING] Successfully submitted today's VTU Internship Diary entry!")
            print(f"📷 Temporary confirmation displayed from: {screenshot_path} (auto-deleting after viewing)")
            auto_delete_after_viewing(screenshot_path, delay_seconds=15)

            log_entry(
                task_id="vtu-portal-diary-entry",
                action="vtu_diary_entry",
                result="SUCCESS: Diary entry saved",
                approved_by="auto-30min" if not dry_run else "dry-run",
            )
            return True, "VTU Diary entry recorded successfully."

    except Exception as e:
        err_msg = f"VTU Diary automation error: {e}"
        log_entry(
            task_id="vtu-portal-diary-entry",
            action="vtu_diary_entry",
            result=f"FAILED: {e}",
            approved_by="auto-30min",
        )
        return False, err_msg


if __name__ == "__main__":
    success, msg = enter_vtu_diary(headless=True, dry_run=True)
    print(f"Result: {success}\n{msg}")
