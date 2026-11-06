"""Batch submitter for VTU Internship Daily Diary entries.

Handles submitting entries from pending_vtu_entries.json date-wise,
verifying previously submitted entries on https://vtu.internyet.in/dashboard/student/diary-entries
to strictly prevent duplicate submissions.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
import time
from typing import Dict, List, Set

from playwright.sync_api import sync_playwright, Page

SIGN_IN_URL = "https://vtu.internyet.in/sign-in"
DIARY_URL = "https://vtu.internyet.in/dashboard/student/student-diary"
ENTRIES_LIST_URL = "https://vtu.internyet.in/dashboard/student/diary-entries"
ENTRIES_FILE = Path(__file__).parent / "pending_vtu_entries.json"


def get_submitted_dates(page: Page) -> Set[str]:
    """Retrieve all dates already submitted on the VTU portal (YYYY-MM-DD)."""
    page.goto(ENTRIES_LIST_URL, wait_until="domcontentloaded")
    page.wait_for_timeout(3000)

    submitted_dates = set()
    rows = page.locator("tr").all_inner_texts()
    for row in rows:
        # e.g. 2026-10-01T00:00:00.000000Z
        parts = row.split()
        for p in parts:
            if "T" in p and len(p) >= 10:
                d_str = p.split("T")[0]
                if len(d_str) == 10 and d_str.startswith("2026-"):
                    submitted_dates.add(d_str)
            elif len(p) == 10 and p.startswith("2026-"):
                submitted_dates.add(p)
    return submitted_dates


def select_date_in_calendar(page: Page, target_dt: datetime) -> bool:
    """Open calendar and click the exact date."""
    page.locator('button:has-text("Pick a Date")').first.click()
    page.wait_for_timeout(500)

    # Check currently displayed month
    caption = page.locator('.rdp-month_caption, .rdp-caption_label, [role="grid"]').first.inner_text()
    
    # If target is October (month 10) and caption is November, click previous month
    if target_dt.month == 10 and "October" not in caption:
        prev_btn = page.locator('button[aria-label*="Previous Month"], .rdp-button_previous').first
        prev_btn.click()
        page.wait_for_timeout(500)
    elif target_dt.month == 11 and "November" not in caption:
        next_btn = page.locator('button[aria-label*="Next Month"], .rdp-button_next').first
        next_btn.click()
        page.wait_for_timeout(500)

    month_name = target_dt.strftime("%B")
    day_num = target_dt.day

    # Match by data-day e.g. "10/2/2026" or aria-label e.g. "October 2"
    selectors = [
        f'button[data-day="{target_dt.month}/{day_num}/{target_dt.year}"]',
        f'button[aria-label*="{month_name} {day_num}"]',
    ]

    for sel in selectors:
        btn = page.locator(sel).first
        if btn.count() > 0 and not btn.get_attribute("disabled"):
            btn.click()
            page.wait_for_timeout(500)
            return True

    return False


def fill_diary_form(page: Page, entry: Dict) -> bool:
    """Fill in all the diary form fields and submit."""
    # Description / Work Summary
    desc_field = page.locator('textarea[name="description"], textarea[placeholder*="describe"]').first
    desc_field.fill(entry["work_summary"])

    # Hours
    hours_field = page.locator('input[placeholder*="6.5"], input[type="number"]').first
    hours_field.fill(entry["hours"])

    # Reference links
    links_field = page.locator('textarea[name="links"], textarea[placeholder*="links"]').first
    links_field.fill(entry["links"])

    # Learnings
    learn_field = page.locator('textarea[name="learnings"], textarea[placeholder*="learn"]').first
    learn_field.fill(entry["learnings"])

    # Blockers
    block_field = page.locator('textarea[name="blockers"], textarea[placeholder*="slowed"]').first
    block_field.fill(entry["blockers"])

    # Skills Used: Always include HTML, CSS, React.js
    skill_input = page.locator('#react-select-2-input, input[id*="react-select"]').first
    required_skills = ["HTML", "CSS", "React.js"]

    for skill in required_skills:
        try:
            skill_input.fill(skill)
            page.wait_for_timeout(400)
            opt = page.locator('[class*="option"]:not(:has-text("No options"))').first
            if opt.count() > 0:
                opt.click()
                selected_count += 1
                page.wait_for_timeout(300)
            else:
                page.keyboard.press("Escape")
                page.wait_for_timeout(200)
        except Exception:
            pass

    page.wait_for_timeout(800)

    # Click Save
    save_btn = page.locator('button:has-text("Save")').first
    if save_btn.count() > 0:
        # Wait up to 5s for save button to be enabled
        try:
            save_btn.wait_for(state="visible", timeout=5000)
            save_btn.click()
            page.wait_for_timeout(3000)
            return True
        except Exception as e:
            print(f"Error clicking save button: {e}")
            return False

    return False


def submit_batch(limit: int = 40, dry_run: bool = False, max_date: str = "2026-11-03"):
    """Submit unrecorded entries up to max_date (default 2026-11-03)."""
    if not ENTRIES_FILE.exists():
        print(f"Error: {ENTRIES_FILE} not found.")
        return

    entries: List[Dict] = json.loads(ENTRIES_FILE.read_text(encoding="utf-8"))
    email = "nitishkumarchimmanakatti@gmail.com"
    password = "Vtu@1234"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 800})

        # Login
        print("Logging in to VTU portal...")
        page.goto(SIGN_IN_URL, wait_until="domcontentloaded")
        page.wait_for_timeout(2000)
        page.locator('input[placeholder*="email"]').first.fill(email)
        page.locator('input[type="password"]').first.fill(password)
        page.locator('button:has-text("Sign In")').first.click()
        page.wait_for_timeout(3500)

        # Check already submitted dates
        submitted = get_submitted_dates(page)
        print(f"Found {len(submitted)} already submitted dates on VTU portal.")
        print(f"Latest submitted: {sorted(list(submitted))[-5:]}")

        count = 0
        for entry in entries:
            date_str = entry["date_str"]

            # User restriction: Strictly do it till November 3 only!
            if date_str > max_date:
                print(f"Reached cutoff date {max_date}. Skipping {date_str}.")
                continue

            if date_str in submitted:
                continue

            dt = datetime.strptime(date_str, "%Y-%m-%d")
            print(f"\nProcessing entry for {date_str} ({entry['display_date']})...")

            # 1. Go to selection page
            page.goto(DIARY_URL, wait_until="domcontentloaded")
            page.wait_for_timeout(2000)

            # 2. Select internship
            page.locator('button:has-text("Choose internship"), [role="combobox"]').first.click()
            page.wait_for_timeout(500)
            page.locator('*:has-text("Web Development Intern")').last.click()
            page.wait_for_timeout(500)

            # 3. Select date in calendar
            success_date = select_date_in_calendar(page, dt)
            if not success_date:
                print(f"❌ Failed to select date {date_str} in calendar.")
                continue

            # 4. Click Continue
            page.locator('button:has-text("Continue")').first.click()
            page.wait_for_timeout(2500)

            if "create-diary-entry" not in page.url:
                print(f"⚠️ Page did not advance to create-diary-entry for {date_str}. URL: {page.url}")
                continue

            if dry_run:
                print(f"[DRY RUN] Would submit entry for {date_str}: {entry['work_summary'][:50]}...")
            else:
                success_fill = fill_diary_form(page, entry)
                if success_fill:
                    print(f"✓ Successfully submitted diary entry for {date_str}!")
                    submitted.add(date_str)
                else:
                    print(f"❌ Failed to save diary entry for {date_str}.")

            count += 1
            if count >= limit:
                print(f"\nReached batch limit of {limit} entries.")
                break

            time.sleep(1.5)

        browser.close()


if __name__ == "__main__":
    import sys
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 40
    submit_batch(limit=limit, dry_run=False, max_date="2026-11-03")
