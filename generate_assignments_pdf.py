import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright
from telegram_notifier import send_telegram_document, send_telegram_message

student_email = os.getenv("VTU_ONLINE_EMAIL") or os.getenv("VTU_EMAIL") or "Registered Student"

ARTIFACT_DIR = Path("/Users/nitishkumarbchimmanakatti/.gemini/antigravity/brain/6ce00d1c-03b2-4d6c-872c-f49c65c23f32")
JSON_PATH = ARTIFACT_DIR / "VTU_Online_Assignments_Full_Review.json"
PDF_PATH = ARTIFACT_DIR / "VTU_Online_Assignments_Full_Review.pdf"
PROJECT_PDF = Path("/Users/nitishkumarbchimmanakatti/Projects/daybook/VTU_Online_Assignments_Full_Review.pdf")

with open(JSON_PATH) as f:
    data = json.load(f)

html_content = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>VTU Online LMS - Complete Assignments Record</title>
<style>
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    color: #1e293b;
    padding: 30px;
    line-height: 1.5;
  }
  h1 { color: #0f172a; border-bottom: 2px solid #3b82f6; padding-bottom: 8px; font-size: 24px; margin-top: 30px; }
  h2 { color: #1e40af; font-size: 18px; margin-top: 20px; }
  .header-box {
    background: #f1f5f9;
    border-radius: 8px;
    padding: 16px 20px;
    margin-bottom: 24px;
    border-left: 4px solid #3b82f6;
  }
  .info-badge {
    display: inline-block;
    padding: 4px 10px;
    border-radius: 6px;
    font-weight: 600;
    font-size: 13px;
    margin-right: 8px;
  }
  .badge-pass { background: #dcfce7; color: #166534; }
  .badge-score { background: #e0f2fe; color: #0369a1; }
  table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 12px;
    font-size: 12px;
  }
  th {
    background: #f8fafc;
    color: #475569;
    text-align: left;
    padding: 8px 10px;
    border-bottom: 2px solid #cbd5e1;
  }
  td {
    padding: 8px 10px;
    border-bottom: 1px solid #e2e8f0;
    vertical-align: top;
  }
  tr:nth-child(even) { background: #fdfdfd; }
  .status-correct { color: #16a34a; font-weight: 600; }
  .status-wrong { color: #dc2626; font-weight: 600; }
  .page-break { page-break-after: always; }
</style>
</head>
<body>
<div class="header-box">
  <h2 style="margin-top:0; color:#0f172a;">VTU Centre for Online Education — Official Course Assignments</h2>
  <div><strong>Platform:</strong> <a href="https://online.vtu.ac.in">https://online.vtu.ac.in</a></div>
  <div><strong>Student Email:</strong> {student_email}</div>
  <div><strong>Structure Note:</strong> Assignments on VTU Online are formatted as online computer-based tests (25 multiple choice questions each) submitted directly via the portal. Below is the complete record of all 100 questions, submitted responses, and evaluation results.</div>
</div>
"""

course_idx = 0
for course_title, exams in data.items():
    if course_idx > 0:
        html_content += '<div class="page-break"></div>'
    course_idx += 1
    html_content += f"<h1>{course_title}</h1>"

    for ex in exams:
        att = ex["attempt_info"]
        html_content += f"<h2>{ex['exam_name']} (Exam ID: {ex['exam_id']})</h2>"
        html_content += f"""<div>
          <span class="info-badge badge-pass">Status: {'Passed' if att.get('is_passed') else 'Submitted'}</span>
          <span class="info-badge badge-score">Score: {att.get('total_correct', 'N/A')} / {att.get('total_questions', '25')} ({att.get('percentage', 'N/A')})</span>
        </div>"""

        html_content += """<table>
          <thead>
            <tr>
              <th style="width: 5%;">#</th>
              <th style="width: 45%;">Question</th>
              <th style="width: 25%;">Submitted Answer</th>
              <th style="width: 25%;">Correct Answer</th>
            </tr>
          </thead>
          <tbody>"""

        for i, q in enumerate(ex["review"], 1):
            is_c = q.get("is_correct")
            sym = '<span class="status-correct">✓ </span>' if is_c else '<span class="status-wrong">✗ </span>'
            html_content += f"""<tr>
              <td>{i}</td>
              <td>{q.get('question')}</td>
              <td>{sym}{q.get('user_answer')}</td>
              <td>{q.get('correct_answer')}</td>
            </tr>"""

        html_content += "</tbody></table><br/>"

html_content += "</body></html>"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.set_content(html_content)
    page.pdf(path=str(PDF_PATH), format="A4", margin={"top": "20mm", "bottom": "20mm", "left": "15mm", "right": "15mm"})
    page.pdf(path=str(PROJECT_PDF), format="A4", margin={"top": "20mm", "bottom": "20mm", "left": "15mm", "right": "15mm"})
    print(f"Generated PDF: {PDF_PATH}")


