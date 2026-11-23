import re
import json
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime

DOCX_PATH = Path("/Users/nitishkumarbchimmanakatti/Projects/daybook/VTU_Edutainer_AI_120_Day_Diary_Until_Nov30_HTML_CSS_ReactJS.docx")
OUT_JSON = Path("/Users/nitishkumarbchimmanakatti/Projects/daybook/diary_entries.json")

def extract_paragraphs(docx_path):
    with zipfile.ZipFile(docx_path) as z:
        xml_content = z.read("word/document.xml")
        tree = ET.fromstring(xml_content)
        # Word paragraphs are <w:p>
        ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
        paragraphs = []
        for p in tree.findall('.//w:p', ns):
            texts = [node.text for node in p.findall('.//w:t', ns) if node.text]
            p_text = "".join(texts).strip()
            if p_text:
                paragraphs.append(p_text)
        return paragraphs

paragraphs = extract_paragraphs(DOCX_PATH)
full_text = "\n".join(paragraphs)

day_blocks = re.split(r'(Day\s+\d+\s*[-—]\s*\d+\s+[A-Za-z]+\s+\d{4})', full_text)

entries = {}
header = None

for block in day_blocks:
    m_header = re.match(r'Day\s+(\d+)\s*[-—]\s*(\d+\s+[A-Za-z]+\s+\d{4})', block.strip())
    if m_header:
        header = (int(m_header.group(1)), m_header.group(2))
        continue
    if header and block.strip():
        day_num, date_str = header
        
        # Parse fields
        def get_field(pat, text, default=""):
            m = re.search(pat, text, re.IGNORECASE)
            return m.group(1).strip() if m else default

        work_summary = get_field(r'Work Summary:\s*(.*?)(?=\nHours Worked:|\nReference Links:|$)', block)
        hours = get_field(r'Hours Worked:\s*(.*?)(?=\nReference Links:|\nLearnings|$)', block, "6.5")
        ref_links = get_field(r'Reference Links:\s*(.*?)(?=\nLearnings|$)', block, "https://www.internship.edutainer.in/student/my-learning")
        learnings = get_field(r'Learnings\s*/\s*Outcomes:\s*(.*?)(?=\nBlockers|$)', block)
        blockers = get_field(r'Blockers\s*/\s*Risks:\s*(.*?)(?=\nSkills Used:|$)', block, "None")
        skills = get_field(r'Skills Used:\s*(.*?)(?=\nDay\s+\d+|$)', block, "HTML, CSS, ReactJS")

        try:
            dt = datetime.strptime(date_str, "%d %B %Y")
            iso_date = dt.strftime("%Y-%m-%d")
        except Exception:
            iso_date = date_str

        entries[iso_date] = {
            "day": day_num,
            "date": date_str,
            "iso_date": iso_date,
            "internship": "Artificial Intelligence Intern (Entry Level) — Edutainer",
            "work_summary": work_summary,
            "hours_worked": hours,
            "reference_links": ref_links,
            "learnings_outcomes": learnings,
            "blockers_risks": blockers,
            "skills_used": skills
        }
        header = None

print(f"Extracted {len(entries)} valid daily entries from docx.")
if entries:
    sample_key = sorted(entries.keys())[0]
    print("Sample Entry:", json.dumps(entries[sample_key], indent=2))
    sample_today = "2026-11-15"
    if sample_today in entries:
        print("Today's Entry (2026-11-15):", json.dumps(entries[sample_today], indent=2))

with open(OUT_JSON, "w") as f:
    json.dump(entries, f, indent=2)
print(f"Saved to {OUT_JSON}")
