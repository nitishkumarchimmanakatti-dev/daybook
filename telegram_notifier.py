"""Telegram notification module for Daybook.

Sends confirmation messages and high-resolution screenshots directly
to the user's phone via Telegram Bot API.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional, Tuple
import urllib.request
import urllib.error

from config import get_daybook_dir

CONFIG_FILE = get_daybook_dir() / ".credentials.json"


def get_telegram_config() -> Tuple[Optional[str], Optional[str]]:
    """Retrieve Telegram Bot Token and Chat ID."""
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        if CONFIG_FILE.exists():
            try:
                data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
                token = token or data.get("telegram_bot_token")
                chat_id = chat_id or data.get("telegram_chat_id")
            except Exception:
                pass

    token = token or "9057161221:AAH4qxnMVVSEAQ7DPsN9tD9EqY-Qc5KA6Mc"
    chat_id = chat_id or "1427324293"

    return token, chat_id


def save_telegram_config(token: str, chat_id: str) -> None:
    """Save Telegram credentials securely."""
    data = {}
    if CONFIG_FILE.exists():
        try:
            data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        except Exception:
            data = {}
    data["telegram_bot_token"] = token
    data["telegram_chat_id"] = chat_id
    CONFIG_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
    CONFIG_FILE.chmod(0o600)


def send_telegram_photo(image_path: Path | str, caption: str = "") -> Tuple[bool, str]:
    """Send an image directly to the user's Telegram."""
    token, chat_id = get_telegram_config()
    if not token or not chat_id:
        return False, "Telegram Bot Token or Chat ID not configured."

    img_path = Path(image_path)
    if not img_path.exists():
        return False, f"Image not found at {img_path}"

    url = f"https://api.telegram.org/bot{token}/sendPhoto"
    boundary = "----WebKitFormBoundaryDaybookNotifier7MA4YWxkTrZu0gW"
    
    body = bytearray()
    
    # chat_id field
    body.extend(f"--{boundary}\r\n".encode("utf-8"))
    body.extend(f'Content-Disposition: form-data; name="chat_id"\r\n\r\n{chat_id}\r\n'.encode("utf-8"))
    
    # caption field
    if caption:
        body.extend(f"--{boundary}\r\n".encode("utf-8"))
        body.extend(f'Content-Disposition: form-data; name="caption"\r\n\r\n{caption}\r\n'.encode("utf-8"))
        
    # photo file field
    filename = img_path.name
    body.extend(f"--{boundary}\r\n".encode("utf-8"))
    body.extend(f'Content-Disposition: form-data; name="photo"; filename="{filename}"\r\n'.encode("utf-8"))
    body.extend(b"Content-Type: image/png\r\n\r\n")
    body.extend(img_path.read_bytes())
    body.extend(b"\r\n")
    
    # end boundary
    body.extend(f"--{boundary}--\r\n".encode("utf-8"))

    req = urllib.request.Request(
        url,
        data=bytes(body),
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            res_data = json.loads(resp.read().decode("utf-8"))
            if res_data.get("ok"):
                return True, "Telegram photo sent successfully."
            return False, f"Telegram API error: {res_data}"
    except Exception as e:
        return False, f"Failed to send Telegram photo: {e}"


def send_telegram_document(document_path: Path | str, caption: str = "") -> Tuple[bool, str]:
    """Send a document (PDF, TXT, MD, etc.) directly to the user's Telegram."""
    token, chat_id = get_telegram_config()
    if not token or not chat_id:
        return False, "Telegram Bot Token or Chat ID not configured."

    doc_path = Path(document_path)
    if not doc_path.exists():
        return False, f"Document not found at {doc_path}"

    url = f"https://api.telegram.org/bot{token}/sendDocument"
    boundary = "----WebKitFormBoundaryDaybookDocNotifier7MA4YWxkTrZu0gW"

    body = bytearray()

    # chat_id field
    body.extend(f"--{boundary}\r\n".encode("utf-8"))
    body.extend(f'Content-Disposition: form-data; name="chat_id"\r\n\r\n{chat_id}\r\n'.encode("utf-8"))

    # caption field
    if caption:
        body.extend(f"--{boundary}\r\n".encode("utf-8"))
        body.extend(f'Content-Disposition: form-data; name="caption"\r\n\r\n{caption}\r\n'.encode("utf-8"))

    # document file field
    filename = doc_path.name
    content_type = "application/pdf" if filename.lower().endswith(".pdf") else "application/octet-stream"
    body.extend(f"--{boundary}\r\n".encode("utf-8"))
    body.extend(f'Content-Disposition: form-data; name="document"; filename="{filename}"\r\n'.encode("utf-8"))
    body.extend(f"Content-Type: {content_type}\r\n\r\n".encode("utf-8"))
    body.extend(doc_path.read_bytes())
    body.extend(b"\r\n")

    # end boundary
    body.extend(f"--{boundary}--\r\n".encode("utf-8"))

    req = urllib.request.Request(
        url,
        data=bytes(body),
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            res_data = json.loads(resp.read().decode("utf-8"))
            if res_data.get("ok"):
                return True, "Telegram document sent successfully."
            return False, f"Telegram API error: {res_data}"
    except Exception as e:
        return False, f"Failed to send Telegram document: {e}"


def send_telegram_message(message: str) -> Tuple[bool, str]:
    """Send a plain text message to the user's Telegram."""
    token, chat_id = get_telegram_config()
    if not token or not chat_id:
        return False, "Telegram Bot Token or Chat ID not configured."

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = json.dumps({"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}).encode("utf-8")
    
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            res_data = json.loads(resp.read().decode("utf-8"))
            if res_data.get("ok"):
                return True, "Telegram message sent successfully."
            return False, f"Telegram API error: {res_data}"
    except Exception as e:
        return False, f"Failed to send Telegram message: {e}"
