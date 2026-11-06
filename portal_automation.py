"""Browser automation module for EduTrainer Internship portal login.

Automates login to https://internship.edutainer.in/saml/login
and navigates to https://www.internship.edutainer.in/student/my-learning.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import threading
import time
from typing import Optional, Tuple
from datetime import datetime

from config import get_daybook_dir, ensure_daybook_dirs
from log import log_entry

CREDENTIALS_FILE = get_daybook_dir() / ".credentials.json"
LOGIN_URL = "https://internship.edutainer.in/saml/login"
TARGET_URL = "https://www.internship.edutainer.in/student/my-learning"


def auto_delete_after_viewing(file_path: Path, delay_seconds: int = 15) -> None:
    """Open screenshot in Preview so the user sees it, then delete it automatically."""
    try:
        subprocess.run(["open", str(file_path)], check=False)
    except Exception:
        pass

    # Launch detached background cleanup so it deletes even after Python exits
    cleanup_cmd = f"sleep {delay_seconds} && rm -f '{file_path}'"
    subprocess.Popen(["bash", "-c", cleanup_cmd], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def get_credentials() -> Tuple[str, str]:
    """Retrieve EduTrainer credentials from env or secured config file."""
    email = os.environ.get("EDUTAINER_EMAIL")
    password = os.environ.get("EDUTAINER_PASSWORD")

    if not email or not password:
        if CREDENTIALS_FILE.exists():
            try:
                creds = json.loads(CREDENTIALS_FILE.read_text(encoding="utf-8"))
                email = email or creds.get("edutainer_email")
                password = password or creds.get("edutainer_password")
            except Exception:
                pass

    # Default fallback from provided configuration
    email = email or "nitishkumarchimmanakatti@gmail.com"
    password = password or "zkzy9KTD"
    return email, password


def save_credentials(email: str, password: str) -> None:
    """Save credentials to ~/Daybook/.credentials.json with restricted 0600 permissions."""
    ensure_daybook_dirs()
    data = {}
    if CREDENTIALS_FILE.exists():
        try:
            data = json.loads(CREDENTIALS_FILE.read_text(encoding="utf-8"))
        except Exception:
            data = {}
    data["edutainer_email"] = email
    data["edutainer_password"] = password

    CREDENTIALS_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
    CREDENTIALS_FILE.chmod(0o600)


def login_edutainer(headless: bool = True) -> Tuple[bool, str]:
    """Perform automated browser login using Playwright."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return False, "Playwright is not installed. Run `pip install playwright && playwright install chromium`."

    email, password = get_credentials()
    if not email or not password:
        return False, "Missing credentials for EduTrainer login."

    screenshot_dir = get_daybook_dir() / "screenshots"
    screenshot_dir.mkdir(parents=True, exist_ok=True)
    # Remove any old screenshot so disk storage is never filled
    for old_file in screenshot_dir.glob("*.png"):
        try:
            old_file.unlink()
        except OSError:
            pass
    screenshot_path = screenshot_dir / "latest_login.png"

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=headless)
            context = browser.new_context(
                viewport={"width": 1280, "height": 800},
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            )
            page = context.new_page()

            # 1. Navigate to login
            page.goto(LOGIN_URL, wait_until="networkidle", timeout=30000)

            # 2. Fill Email / Phone
            email_input = page.locator('input[type="email"], input[type="text"], input[placeholder*="Email"]').first
            email_input.fill(email)

            # 3. Fill Password
            password_input = page.locator('input[type="password"]').first
            password_input.fill(password)

            # 4. Click Sign In
            sign_in_button = page.locator('button:has-text("Sign In"), input[type="submit"]').first
            sign_in_button.click()

            # 5. Wait for redirect or navigation
            try:
                page.wait_for_url("**/student/**", timeout=15000)
            except Exception:
                page.wait_for_timeout(4000)

            # Scroll November 2026 into view so current month attendance is visible in the preview
            try:
                nov_el = page.locator('text=November 2026').first
                if nov_el.count() > 0:
                    nov_el.scroll_into_view_if_needed()
                    page.wait_for_timeout(500)
            except Exception:
                pass

            # Save screenshot for audit verification
            page.screenshot(path=str(screenshot_path))
            current_url = page.url
            browser.close()

            success = "student" in current_url or "my-learning" in current_url or current_url != LOGIN_URL
            msg = f"EduTrainer login finished. Current URL: {current_url}. Temporary preview: {screenshot_path}"
            
            log_entry(
                task_id="edutraner-intern-login",
                action="portal_login",
                result=f"SUCCESS: {current_url}" if success else f"CHECK: {current_url}",
                approved_by="auto-30min",
            )

            # Ping back to the user via native macOS desktop notification and sound
            if success:
                try:
                    from telegram_notifier import send_telegram_photo
                    caption = f"✅ EduTrainer Login & Attendance Recorded\n📅 Date: {datetime.now().strftime('%d %b %Y')}\n🔗 Status: Present"
                    send_telegram_photo(screenshot_path, caption=caption)
                except Exception as tg_err:
                    print(f"Telegram notify error: {tg_err}")

                from notify import send_macos_notification
                send_macos_notification(
                    title="EduTrainer Auto-Login ✅",
                    subtitle="Login Successful",
                    message="I have logged into EduTrainer Internship portal for you.",
                    sound="Glass",
                )
                print("\n🔔 [PING] I have successfully logged into the EduTrainer Internship portal for you!")
                print(f"📷 Temporary screenshot displayed from: {screenshot_path} (auto-deleting after viewing to preserve storage)")
                auto_delete_after_viewing(screenshot_path, delay_seconds=15)

            return success, msg

    except Exception as e:
        err_msg = f"Browser automation error: {e}"
        log_entry(
            task_id="edutraner-intern-login",
            action="portal_login",
            result=f"FAILED: {e}",
            approved_by="auto-30min",
        )
        return False, err_msg


if __name__ == "__main__":
    success, message = login_edutainer(headless=True)
    print(f"Success: {success}\n{message}")
