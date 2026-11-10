"""Script to generate a comprehensive, publication-quality PDF handbook
of all 20 modules and 67 lectures of 'Python Essentials and Libraries for Data Science'
and send the document directly to the student's Telegram bot.
"""

from pathlib import Path
from playwright.sync_api import sync_playwright
from telegram_notifier import send_telegram_document, send_telegram_message

HTML_CONTENT = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Python Essentials and Libraries for Data Science - Complete Course Handbook</title>
<style>
    @page {
        size: A4;
        margin: 18mm 16mm 20mm 16mm;
        @bottom-right {
            content: "Page " counter(page);
            font-size: 9pt;
            color: #64748b;
        }
    }
    body {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        color: #1e293b;
        line-height: 1.55;
        font-size: 10.5pt;
        margin: 0;
        padding: 0;
    }
    .cover-page {
        page-break-after: always;
        height: 90vh;
        display: flex;
        flex-direction: column;
        justify-content: center;
        border-bottom: 4px solid #3b82f6;
        padding-bottom: 40px;
    }
    .cover-title {
        font-size: 28pt;
        font-weight: 800;
        color: #0f172a;
        line-height: 1.2;
        margin-bottom: 12px;
    }
    .cover-subtitle {
        font-size: 15pt;
        color: #3b82f6;
        font-weight: 600;
        margin-bottom: 25px;
    }
    .meta-box {
        background: #f8fafc;
        border-left: 4px solid #3b82f6;
        padding: 16px 20px;
        margin: 25px 0;
        border-radius: 0 8px 8px 0;
    }
    .meta-box p {
        margin: 6px 0;
        font-size: 11pt;
    }
    .meta-box strong {
        color: #0f172a;
    }
    h1.module-header {
        font-size: 16pt;
        font-weight: 700;
        color: #ffffff;
        background: linear-gradient(135deg, #1e3a8a, #2563eb);
        padding: 10px 14px;
        border-radius: 6px;
        margin-top: 30px;
        margin-bottom: 16px;
        page-break-after: avoid;
    }
    .lesson-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 6px;
        padding: 12px 16px;
        margin-bottom: 14px;
        page-break-inside: avoid;
    }
    .lesson-title {
        font-size: 12pt;
        font-weight: 700;
        color: #1e40af;
        margin-top: 0;
        margin-bottom: 6px;
        border-bottom: 1px solid #f1f5f9;
        padding-bottom: 4px;
    }
    .concept-text {
        margin: 6px 0;
        color: #334155;
    }
    pre {
        background: #0f172a;
        color: #f8fafc;
        padding: 10px 12px;
        border-radius: 5px;
        font-family: "SF Mono", Menlo, Consolas, Monaco, monospace;
        font-size: 9pt;
        overflow-x: auto;
        margin: 8px 0;
        line-height: 1.4;
    }
    code {
        font-family: "SF Mono", Menlo, Consolas, Monaco, monospace;
        background: #f1f5f9;
        color: #0f172a;
        padding: 2px 5px;
        border-radius: 3px;
        font-size: 9.5pt;
    }
    pre code {
        background: transparent;
        color: inherit;
        padding: 0;
    }
    .bullet-points {
        margin: 6px 0 6px 18px;
        padding: 0;
    }
    .bullet-points li {
        margin-bottom: 4px;
    }
    .tag {
        display: inline-block;
        font-size: 8pt;
        font-weight: 600;
        padding: 2px 7px;
        border-radius: 4px;
        background: #e0e7ff;
        color: #3730a3;
        margin-right: 6px;
    }
</style>
</head>
<body>

<div class="cover-page">
    <div class="cover-title">Python Essentials &amp; Libraries for Data Science</div>
    <div class="cover-subtitle">Complete 20-Module Comprehensive Reference Handbook (67 Lectures)</div>
    
    <div class="meta-box">
        <p><strong>Student Name:</strong> Nitishkumar Balappa Chimmanakatti</p>
        <p><strong>Internship Domain:</strong> Artificial Intelligence &amp; Data Science (Entry Level)</p>
        <p><strong>Training Portal:</strong> EduTrainer Internship Portal (100% Course Completed)</p>
        <p><strong>Affiliated University:</strong> Visvesvaraya Technological University (VTU)</p>
        <p><strong>Modules Covered:</strong> 20 Modules | 67 Lectures | Full Hands-on Code &amp; Theory</p>
    </div>

    <p style="color: #64748b; font-size: 10pt; margin-top: 40px;">
        This document provides comprehensive technical reference notes for all core Python constructs, object-oriented design, graphical interfaces, file handling, relational database connections, and full data science pipelines (NumPy, Pandas, Matplotlib, Seaborn, Scikit-Learn, and Django).
    </p>
</div>

<!-- MODULE 1 -->
<h1 class="module-header">Module 1: Python Introduction, Setup &amp; Basic Syntax</h1>

<div class="lesson-card">
    <div class="lesson-title">Lesson 1: Python Introduction and Basic Syntax</div>
    <p class="concept-text">Python is an interpreted, high-level, dynamically typed language developed by Guido van Rossum. It uses clean indentation rather than curly brackets for block scoping.</p>
    <ul class="bullet-points">
        <li><strong>Execution Model:</strong> Source code (<code>.py</code>) compiles to intermediate bytecode (<code>.pyc</code>), executed by the Python Virtual Machine (PVM).</li>
        <li><strong>Philosophy:</strong> Readability counts, explicit is better than implicit (PEP 20 - Zen of Python).</li>
    </ul>
<pre><code>print("Hello, Data Science!")  # Outputs text to standard stdout
name = "Nitish"                # Variable binding without type declaration</code></pre>
</div>

<div class="lesson-card">
    <div class="lesson-title">Lesson 2: Python Installation &amp; Environment Setup</div>
    <p class="concept-text">Configuring Python 3 runtime, the <code>pip</code> package installer, virtual environments, and code editors.</p>
    <ul class="bullet-points">
        <li><code>pip install &lt;package&gt;</code>: Installs third-party wheels from the Python Package Index (PyPI).</li>
        <li><code>python3 -m venv myenv</code>: Creates an isolated directory for dependencies, preventing system library conflicts.</li>
    </ul>
<pre><code># Virtual environment setup
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux</code></pre>
</div>

<div class="lesson-card">
    <div class="lesson-title">Lesson 3: Python Variables &amp; Memory Allocation</div>
    <p class="concept-text">Variables in Python are reference tags pointing to objects in heap memory. Assignment does not copy data; it creates a reference.</p>
    <ul class="bullet-points">
        <li><code>id(obj)</code>: Returns the memory address of the object.</li>
        <li>Dynamic typing allows a variable to reference different types throughout its lifecycle.</li>
    </ul>
<pre><code>x = 250        # Integer object allocated in heap
y = x          # y points to the exact same memory address as x
print(id(x) == id(y))  # True</code></pre>
</div>

<div class="lesson-card">
    <div class="lesson-title">Lesson 4: Python Data Types and Conditional Statements</div>
    <p class="concept-text">Fundamental built-in primitive types: <code>int</code>, <code>float</code>, <code>str</code>, <code>bool</code>, and basic decision branches with <code>if-elif-else</code>.</p>
<pre><code>score = 88.5
if score &gt;= 90:
    grade = 'A'
elif score &gt;= 75:
    grade = 'B'
else:
    grade = 'C'</code></pre>
</div>

<!-- MODULE 2 -->
<h1 class="module-header">Module 2: Control Flow &amp; Fundamental Collections</h1>

<div class="lesson-card">
    <div class="lesson-title">Lesson 5: Conditional and Logical Statements</div>
    <p class="concept-text">Boolean logic expressions utilizing relational operators (<code>==</code>, <code>!=</code>, <code>&lt;</code>, <code>&gt;=</code>) and logical operators (<code>and</code>, <code>or</code>, <code>not</code>).</p>
<pre><code>age = 21
has_id = True
if age &gt;= 18 and has_id:
    print("Eligible for registration")</code></pre>
</div>

<div class="lesson-card">
    <div class="lesson-title">Lessons 6 &amp; 7: Python Loops (while and for)</div>
    <p class="concept-text">Iteration constructs: <code>while</code> loops execute while a condition remains true; <code>for</code> loops iterate over sequential collections using Python's iterator protocol.</p>
<pre><code># while loop
count = 3
while count &gt; 0:
    print(count)
    count -= 1

# for loop over sequence
for item in ["NumPy", "Pandas", "Matplotlib"]:
    print(f"Library: {item}")</code></pre>
</div>

<div class="lesson-card">
    <div class="lesson-title">Lessons 8 &amp; 9: Lists, Tuples, Dictionaries, and Sets</div>
    <ul class="bullet-points">
        <li><strong>List (<code>[]</code>):</strong> Ordered, mutable, indexed. Supports <code>append()</code>, <code>insert()</code>, <code>pop()</code>, and slicing <code>[start:end:step]</code>.</li>
        <li><strong>Tuple (<code>()</code>):</strong> Ordered, immutable. Safe for fixed constants and dictionary keys.</li>
        <li><strong>Dictionary (<code>{}</code>):</strong> Key-value hash map providing average O(1) time complexity lookups.</li>
        <li><strong>Set (<code>{}</code>):</strong> Unordered collection of unique items. Supports mathematical union (<code>|</code>) and intersection (<code>&amp;</code>).</li>
    </ul>
<pre><code>skills_list = ["HTML", "CSS", "React.js"]
student_dict = {"name": "Nitish", "hours": 6.5, "status": "active"}
unique_tags = {"AI", "ML", "Python", "AI"}  # Drops duplicate 'AI'</code></pre>
</div>

<!-- MODULE 3 -->
<h1 class="module-header">Module 3: Loop Controls &amp; Nested Structures</h1>

<div class="lesson-card">
    <div class="lesson-title">Lessons 10, 11 &amp; 12: Break, Continue &amp; Nested Data</div>
    <ul class="bullet-points">
        <li><strong><code>break</code>:</strong> Exits the innermost loop immediately.</li>
        <li><strong><code>continue</code>:</strong> Skips remaining statements in the current iteration and begins the next.</li>
        <li><strong>Nested Structures:</strong> Matrix representations via lists of lists or lists of dictionaries.</li>
    </ul>
<pre><code>for num in range(1, 10):
    if num == 3:
        continue  # Skip 3
    if num == 7:
        break     # Stop loop at 7
    print(num, end=" ")</code></pre>
</div>

<!-- MODULE 4 -->
<h1 class="module-header">Module 4: Functions &amp; Functional Programming</h1>

<div class="lesson-card">
    <div class="lesson-title">Lessons 13 &amp; 14: User-Defined Functions and Scoping</div>
    <p class="concept-text">Functions bundle modular, testable logic. Scoping follows the LEGB rule (Local, Enclosing, Global, Built-in).</p>
<pre><code>def calculate_stats(numbers: list) -&gt; tuple:
    total = sum(numbers)
    mean = total / len(numbers) if numbers else 0
    return total, mean  # Returns packed tuple</code></pre>
</div>

<div class="lesson-card">
    <div class="lesson-title">Lessons 15, 16 &amp; 17: Standard Libraries &amp; Functional Constructs</div>
    <p class="concept-text">Higher-order functional tools allow expressive, vectorized-style operations on collections.</p>
<pre><code>numbers = [1, 2, 3, 4, 5]
squares = list(map(lambda x: x**2, numbers))        # [1, 4, 9, 16, 25]
evens = list(filter(lambda x: x % 2 == 0, numbers))  # [2, 4]</code></pre>
</div>

<!-- MODULES 5 & 6 -->
<h1 class="module-header">Modules 5 &amp; 6: Object-Oriented Programming (OOP)</h1>

<div class="lesson-card">
    <div class="lesson-title">Lessons 18–20: Classes, Objects &amp; Constructors</div>
    <p class="concept-text">Classes encapsulate state (attributes) and behavior (methods). The <code>__init__</code> method initializes new instance state.</p>
<pre><code>class ModelPipeline:
    def __init__(self, name: str):
        self.name = name
        self.trained = False

    def train(self):
        self.trained = True
        return f"{self.name} successfully trained."</code></pre>
</div>

<div class="lesson-card">
    <div class="lesson-title">Lessons 21–23: Encapsulation, Inheritance &amp; Polymorphism</div>
    <ul class="bullet-points">
        <li><strong>Encapsulation:</strong> Hiding internal details using leading underscores (<code>_internal</code>, <code>__private</code>).</li>
        <li><strong>Inheritance:</strong> Reusing parent functionality with <code>class Child(Parent):</code> and <code>super().__init__()</code>.</li>
        <li><strong>Polymorphism:</strong> Standard interface where derived classes implement their own specialized logic.</li>
    </ul>
<pre><code>class BaseEvaluator:
    def evaluate(self, y_true, y_pred):
        raise NotImplementedError

class AccuracyEvaluator(BaseEvaluator):
    def evaluate(self, y_true, y_pred):
        return sum(t == p for t, p in zip(y_true, y_pred)) / len(y_true)</code></pre>
</div>

<!-- MODULES 7 & 8 -->
<h1 class="module-header">Modules 7 &amp; 8: Modules, Packages, File I/O &amp; Databases</h1>

<div class="lesson-card">
    <div class="lesson-title">Lessons 24–26: Modules and Packages</div>
    <p class="concept-text">Modules are single <code>.py</code> files; packages are directories containing multiple modules plus an <code>__init__.py</code> marker file.</p>
</div>

<div class="lesson-card">
    <div class="lesson-title">Lessons 27–30: File Handling &amp; Database Connectivity</div>
    <p class="concept-text">Robust file processing with context managers and relational database integration using Python DB-API 2.0.</p>
<pre><code># Safe file I/O using with context
with open("data.csv", "w", encoding="utf-8") as f:
    f.write("date,hours,status\\n2026-11-10,6.5,Present\\n")

# Database connectivity (SQLite example)
import sqlite3
conn = sqlite3.connect("internship.db")
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS diary (date TEXT, hours REAL)")
cursor.execute("INSERT INTO diary VALUES (?, ?)", ("2026-11-10", 6.5))
conn.commit()
conn.close()</code></pre>
</div>

<!-- MODULES 9–11 -->
<h1 class="module-header">Modules 9–11: GUI, Exceptions &amp; Advanced Python</h1>

<div class="lesson-card">
    <div class="lesson-title">Lessons 31 &amp; 32: Desktop GUI with Tkinter</div>
    <p class="concept-text">Event-driven desktop interface development utilizing Tkinter widgets (<code>Tk</code>, <code>Label</code>, <code>Button</code>, <code>Entry</code>) and layout managers (<code>pack</code>, <code>grid</code>).</p>
</div>

<div class="lesson-card">
    <div class="lesson-title">Lessons 33 &amp; 34: Exception Handling Architecture</div>
    <p class="concept-text">Interception of runtime faults using <code>try-except-else-finally</code> guarantees resource cleanup and fault tolerance.</p>
<pre><code>try:
    val = int("123")
except ValueError as e:
    print(f"Parsing error: {e}")
else:
    print("Execution succeeded without error")
finally:
    print("Always executes (closing handles, sockets)")</code></pre>
</div>

<div class="lesson-card">
    <div class="lesson-title">Lessons 35–38: `*args`, `**kwargs`, Generators, Decorators &amp; Threads</div>
    <ul class="bullet-points">
        <li><code>*args, **kwargs</code>: Accept variable positional and keyword arguments.</li>
        <li><strong>Generators:</strong> Memory-efficient stream iterators using <code>yield</code> without loading all values into RAM.</li>
        <li><strong>Decorators:</strong> Meta-programming wrappers extending function behavior (e.g. logging, timers).</li>
        <li><strong>Multithreading:</strong> Concurrency for I/O-bound operations using <code>threading.Thread</code>.</li>
    </ul>
<pre><code># Decorator pattern
def log_execution(func):
    def wrapper(*args, **kwargs):
        print(f"Calling: {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

@log_execution
def train_model():
    return "Training complete"</code></pre>
</div>

<!-- MODULE 12 -->
<h1 class="module-header">Module 12: Web Development Fundamentals with Django</h1>

<div class="lesson-card">
    <div class="lesson-title">Lessons 39–41: Django MVT Framework</div>
    <p class="concept-text">Full-stack web architecture using Django's Model-View-Template pattern:</p>
    <ul class="bullet-points">
        <li><strong>Model:</strong> Python class representing database schema via Django ORM.</li>
        <li><strong>View:</strong> Business logic handler processing HTTP requests and returning HTTP responses.</li>
        <li><strong>Template:</strong> HTML presentation layer rendered with dynamic context variables.</li>
        <li><strong>URLs:</strong> Regular expression/path routing mapping URLs to view functions.</li>
    </ul>
</div>

<!-- MODULE 13 -->
<h1 class="module-header">Module 13: Numerical Computing with NumPy</h1>

<div class="lesson-card">
    <div class="lesson-title">Lessons 42–44: Jupyter Notebooks &amp; NumPy Arrays</div>
    <p class="concept-text">NumPy provides contiguous C-memory homogeneous N-dimensional arrays (<code>ndarray</code>) that compute 50x–100x faster than native Python lists.</p>
<pre><code>import numpy as np

# Array creation &amp; vectorized computation
arr = np.array([1, 2, 3, 4, 5])
scaled = arr * 2.5               # Vectorized operation (no explicit loop)
matrix = np.arange(1, 10).reshape((3, 3))
print("Mean:", np.mean(matrix))
print("Std Dev:", np.std(matrix))</code></pre>
</div>

<!-- MODULE 14 -->
<h1 class="module-header">Module 14: Tabular Data Science with Pandas</h1>

<div class="lesson-card">
    <div class="lesson-title">Lessons 45–47: Series, DataFrames &amp; Data Cleaning</div>
    <p class="concept-text">Pandas is the industry standard for tabular data manipulation, alignment, aggregation, and missing-data imputation.</p>
<pre><code>import pandas as pd

# DataFrame operations
df = pd.DataFrame({
    'date': ['2026-11-08', '2026-11-09', '2026-11-10'],
    'hours': [6.5, 6.5, 6.5],
    'status': ['Present', 'Present', 'Present']
})

# Filtering &amp; Aggregations
active = df[df['hours'] &gt;= 6.0]
total_hours = df['hours'].sum()
print("Summary stats:\\n", df.describe())</code></pre>
</div>

<!-- MODULES 15 & 16 -->
<h1 class="module-header">Modules 15 &amp; 16: Data Visualization (Matplotlib &amp; Seaborn)</h1>

<div class="lesson-card">
    <div class="lesson-title">Lessons 48–51: Charts, Distributions &amp; Correlation Heatmaps</div>
    <p class="concept-text">Visual storytelling using Matplotlib for 2D line/scatter/bar plots and Seaborn for high-level statistical distributions and heatmaps.</p>
<pre><code>import matplotlib.pyplot as plt
import seaborn as sns

# Plotting sample distribution
data = [12, 15, 14, 18, 19, 24, 28, 30]
plt.figure(figsize=(6, 3.5))
plt.plot(data, marker='o', color='#2563eb', label='Trajectory')
plt.title("Sample Performance Curve")
plt.xlabel("Index")
plt.ylabel("Value")
plt.grid(True)
plt.legend()
plt.tight_layout()
# plt.savefig('chart.png')</code></pre>
</div>

<!-- MODULE 17 -->
<h1 class="module-header">Module 17: Data Wrangling &amp; Scikit-Learn Machine Learning</h1>

<div class="lesson-card">
    <div class="lesson-title">Lessons 52–54: Data Wrangling &amp; ML Pipelines</div>
    <p class="concept-text">Data wrangling standardizes raw, messy inputs into analysis-ready features. Scikit-Learn implements consistent estimator interfaces:</p>
    <ul class="bullet-points">
        <li><code>fit(X, y)</code>: Estimates model weights/coefficients from training data.</li>
        <li><code>transform(X)</code>: Transforms features (scaling, normalization, encoding).</li>
        <li><code>predict(X)</code>: Generates predictions on unseen data.</li>
    </ul>
<pre><code>from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression

# Train/test split and modeling workflow
# X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
# model = LinearRegression().fit(X_train, y_train)
# predictions = model.predict(X_test)</code></pre>
</div>

<!-- MODULES 18–20 -->
<h1 class="module-header">Modules 18–20: Coding Challenges, RegEx &amp; Capstone Projects</h1>

<div class="lesson-card">
    <div class="lesson-title">Lessons 55–61: Graphics, Regular Expressions &amp; Algorithmic Challenges</div>
    <p class="concept-text">Turtle graphics for spatial coordinate rendering; <code>re</code> module for regex pattern matching, email validation, and text extraction.</p>
<pre><code>import re

text = "Contact student at nitishkumarchimmanakatti@gmail.com on 2026-11-10"
email_match = re.search(r'[\\w\\.-]+@[\\w\\.-]+\\.\\w+', text)
if email_match:
    print("Found email:", email_match.group(0))</code></pre>
</div>

<div class="lesson-card">
    <div class="lesson-title">Lessons 62–67: Capstone Mini-Projects (Data Science Pipeline)</div>
    <p class="concept-text">Six progressive capstone implementations executing the complete data lifecycle:</p>
    <ul class="bullet-points">
        <li><strong>Project 1:</strong> Command-line CSV statistics extractor with input validation.</li>
        <li><strong>Project 2:</strong> Data cleaning &amp; transformation engine for missing values and outliers.</li>
        <li><strong>Project 3:</strong> Automated exploratory data analysis generating PDF visualization decks.</li>
        <li><strong>Project 4:</strong> Interactive dashboard module displaying filtered KPIs.</li>
        <li><strong>Project 5:</strong> Predictive regression/classification model with evaluation metrics (MSE, R², F1).</li>
        <li><strong>Project 6:</strong> End-to-end production pipeline: Ingestion &rarr; Wrangling &rarr; Model &rarr; Reporting.</li>
    </ul>
</div>

</body>
</html>
"""

def generate_pdf_and_send():
    output_dir = Path("/Users/nitishkumarbchimmanakatti/.gemini/antigravity/brain/6ce00d1c-03b2-4d6c-872c-f49c65c23f32")
    html_path = output_dir / "edutainer_python_complete_notes.html"
    pdf_path = output_dir / "Python_Essentials_and_Data_Science_Complete_Notes.pdf"
    
    html_path.write_text(HTML_CONTENT, encoding="utf-8")
    print(f"Written HTML content to: {html_path}")

    print("Rendering high-resolution A4 PDF via Playwright...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(f"file://{html_path}")
        page.wait_for_timeout(2000)
        
        page.pdf(
            path=str(pdf_path),
            format="A4",
            print_background=True,
            margin={"top": "16mm", "bottom": "18mm", "left": "15mm", "right": "15mm"}
        )
        browser.close()
        print(f"Generated PDF successfully at: {pdf_path}")

    # Send document directly to Telegram
    caption = (
        "📚 Python Essentials & Libraries for Data Science\n"
        "🎓 Complete Course Handbook (20 Modules / 67 Lectures)\n"
        "👤 Student: Nitishkumar Balappa Chimmanakatti\n"
        "✅ Includes all code examples, theory & capstone summaries"
    )
    print("Sending PDF document to Telegram bot...")
    res, msg = send_telegram_document(pdf_path, caption=caption)
    print("Telegram Document Send Result:", res, msg)


if __name__ == "__main__":
    generate_pdf_and_send()
