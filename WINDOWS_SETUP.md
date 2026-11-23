# Daybook Automation — Windows Setup Guide 🚀

This guide explains step-by-step how to set up and run this automation project on a **Windows laptop**.

---

## 📋 What This Project Does

1. **VTU Online LMS Courses (`online.vtu.ac.in`)**:
   - Automatically watches and completes **100% of video lectures** across all modules for enrolled subjects (*Wastewater Treatment & Recycling* and *Privacy & Security in Online Social Media*).
2. **EduTrainer Internship (`internship.edutainer.in`)**:
   - Automatically completes recorded video classes up to **100% progress**.
3. **VTU InternYet Daily Diary (`vtu.internyet.in`)**:
   - Automatically fills and submits the official daily internship diary entry for today's date from the pre-verified 120-day database (`diary_entries.json` / Word document).
   - Fills all fields: Work Summary, Hours Worked (6.5), Reference Links, Learnings / Outcomes, Blockers / Risks, and Skills Used (`HTML, CSS, ReactJS`).
   - Prevents duplicate submissions.
4. **Telegram Notifications (Optional)**:
   - Sends real-time confirmations, progress alerts, and verification screenshots directly to your Telegram bot.

---

## 🛠️ Step 1: Install Python (If not already installed)

1. Download **Python 3.10+** from [python.org](https://www.python.org/downloads/).
2. Run the installer.
3. ⚠️ **IMPORTANT**: On the first screen of the installer, check the box:
   > **☑️ Add python.exe to PATH**
4. Click **Install Now** and wait for completion.

---

## 📥 Step 2: Download or Clone the Project

### Option A: Using Git (Recommended)
Open **PowerShell** or **Command Prompt** and run:
```cmd
git clone https://github.com/nitishkumarchimmanakatti-dev/daybook.git
cd daybook
```

### Option B: Download ZIP
1. Go to the GitHub repository: `https://github.com/nitishkumarchimmanakatti-dev/daybook`
2. Click **Code** -> **Download ZIP**.
3. Extract the ZIP to your desired folder (e.g., `C:\Projects\daybook`).
4. Open the extracted folder.

---

## ⚡ Step 3: Run the Automatic Setup

In the `daybook` folder, simply **double-click** the file:
```
setup_windows.bat
```

*This will automatically:*
* Upgrade `pip`
* Install all required libraries (`playwright`, `pyyaml`, `python-dotenv`)
* Download the headless Chromium browser (`playwright install chromium`)
* Create your personal `.env` configuration file

*(Alternatively, you can manually run in CMD / PowerShell)*:
```cmd
pip install -r requirements.txt
playwright install chromium
copy .env.example .env
```

---

## 🔑 Step 4: Configure Your Credentials (`.env`)

Open the `.env` file in Notepad (or any text editor) and enter your login details:

```env
# VTU Online LMS (https://online.vtu.ac.in)
VTU_ONLINE_EMAIL=your_email@gmail.com
VTU_ONLINE_PASSWORD=your_password

# EduTrainer Internship Platform (https://internship.edutainer.in)
EDUTAINER_EMAIL=your_email@gmail.com
EDUTAINER_PASSWORD=your_password

# VTU InternYet Portal (https://vtu.internyet.in)
VTU_EMAIL=your_email@gmail.com
VTU_PASSWORD=your_password

# Telegram Notifications (Optional - leave empty if not used)
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
```

Save and close the file.

---

## 🚀 Step 5: Run Your Tasks

You can run any task by **double-clicking** the corresponding `.bat` file:

### 1. Complete VTU Online Courses (100% Video Progress)
Double-click:
```
run_vtu_courses.bat
```
*(Or in terminal: `python complete_all_courses_perfect.py`)*  
* **What it does**: Logs into `online.vtu.ac.in`, pulses progress on all 95 lectures across both courses in parallel batches until every lecture hits $\ge 90\%$ and is marked completed, then saves full verification screenshots in the `screenshots/` folder.

---

### 2. Complete EduTrainer Courses (100% Video Progress)
Double-click:
```
run_edutainer_courses.bat
```
*(Or in terminal: `python complete_edutainer_courses.py`)*  
* **What it does**: Logs into `internship.edutainer.in`, completes all recorded lectures for Python Essentials, Full Stack, and React JS, and saves progress screenshots in `screenshots/`.

---

### 3. Submit Today's VTU Internship Diary Entry
Double-click:
```
run_daily_diary.bat
```
*(Or in terminal: `python main.py vtudiary`)*  
* **What it does**: Logs into `vtu.internyet.in`, checks if today's date is already recorded. If not, fills all sections from the 120-day diary database, submits the entry, captures the confirmation screenshot, and sends a notification.

---

## ⏰ Step 6: Automatic Daily Scheduling on Windows (Optional)

If you want Windows to automatically submit your diary every day at 11:30 AM without you having to click anything:

1. Press **Win + R**, type `taskschd.msc`, and press **Enter** to open **Task Scheduler**.
2. Click **Create Basic Task...** on the right side.
3. **Name**: `Daily VTU Diary Submission`.
4. **Trigger**: Select **Daily** -> Set time to `11:30:00 AM`.
5. **Action**: Select **Start a program**.
   * **Program/script**: `python` (or `C:\Python311\python.exe` / path to python).
   * **Add arguments**: `main.py vtudiary`
   * **Start in**: `C:\Projects\daybook` (the absolute path to your daybook folder).
6. Click **Finish**.

Now your laptop will automatically submit your diary entry every day!

---

## ❓ Troubleshooting & FAQs

* **Q: `'python' is not recognized as an internal or external command`**  
  * *Fix*: Re-run the Python installer, choose "Modify", and make sure "Add Python to PATH" is checked. Restart your terminal/computer.
* **Q: Playwright error: `Executable doesn't exist`**  
  * *Fix*: Open Command Prompt in the folder and run: `playwright install chromium`.
* **Q: Where are the verification screenshots saved?**  
  * *Answer*: All screenshots are saved in the `daybook\screenshots` folder.
