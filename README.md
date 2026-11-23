# Daybook — VTU & EduTrainer Automation Suite

An automated workflow system for VTU Online LMS course progress, EduTrainer recorded classes, and daily VTU InternYet diary entries with Telegram alerts.

---

## 💻 Windows Setup (For Windows Laptops)

If you are setting this up on a Windows laptop, see the detailed step-by-step guide:
👉 **[WINDOWS_SETUP.md](WINDOWS_SETUP.md)**

### Quick Start for Windows:
1. Clone or download this repository.
2. Double-click `setup_windows.bat` (installs dependencies & browser).
3. Open `.env` in Notepad and add your portal credentials.
4. Double-click any of the runners:
   - `run_vtu_courses.bat` : Complete 100% of VTU Online course videos
   - `run_edutainer_courses.bat` : Complete 100% of EduTrainer course videos
   - `run_daily_diary.bat` : Submit today's VTU Internship Diary entry

---

## 🍏 macOS / Linux Setup

```bash
git clone https://github.com/nitishkumarchimmanakatti-dev/daybook.git
cd daybook
pip install -r requirements.txt
playwright install chromium
cp .env.example .env
# Edit .env with your credentials
python complete_all_courses_perfect.py
python main.py vtudiary
```

---

## 📁 Key Files & Directories

* `complete_all_courses_perfect.py`: 100% course video lecture completion for VTU Online LMS (`online.vtu.ac.in`).
* `complete_edutainer_courses.py`: 100% video lecture completion for EduTrainer (`internship.edutainer.in`).
* `main.py vtudiary`: Submits today's official VTU Internship Diary entry from the 120-day verified database (`vtu.internyet.in`).
* `diary_entries.json`: Pre-compiled 120-day daily diary content until 30 November 2026.
* `VTU_Online_Assignments_Full_Review.pdf`: Complete question-by-question review of all 4 VTU online course assignments.
* `telegram_notifier.py`: Real-time Telegram notification and screenshot dispatcher.
