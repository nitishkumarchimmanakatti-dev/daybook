"""Script to generate comprehensive, professional PDF notes for all three EduTrainer courses
and send the document directly to the student's Telegram bot.
"""

from __future__ import annotations

import json
from pathlib import Path
from playwright.sync_api import sync_playwright

from telegram_notifier import send_telegram_document, send_telegram_message

HTML_CONTENT = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>EduTrainer Internship Complete Course Notes</title>
<style>
  @page {
    size: A4;
    margin: 20mm 15mm 20mm 15mm;
    @bottom-right {
      content: counter(page);
    }
  }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    line-height: 1.6;
    color: #1e293b;
    font-size: 11pt;
    margin: 0;
    padding: 0;
  }
  .cover {
    page-break-after: always;
    text-align: center;
    padding-top: 80px;
  }
  .cover h1 {
    font-size: 28pt;
    color: #0f172a;
    margin-bottom: 10px;
    font-weight: 800;
  }
  .cover h2 {
    font-size: 16pt;
    color: #2563eb;
    margin-bottom: 30px;
    font-weight: 600;
  }
  .cover .meta-box {
    display: inline-block;
    text-align: left;
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 20px 30px;
    margin-top: 40px;
    font-size: 11pt;
  }
  .cover .meta-box p {
    margin: 6px 0;
  }
  h2.section-header {
    background: #1e293b;
    color: #ffffff;
    padding: 10px 15px;
    border-radius: 6px;
    font-size: 15pt;
    margin-top: 30px;
    page-break-before: always;
  }
  h3.module-header {
    color: #1e40af;
    border-bottom: 2px solid #bfdbfe;
    padding-bottom: 5px;
    font-size: 13pt;
    margin-top: 25px;
  }
  .lesson-card {
    background: #ffffff;
    border-left: 4px solid #3b82f6;
    padding: 8px 14px;
    margin: 12px 0;
    background-color: #f8fafc;
    border-radius: 0 6px 6px 0;
  }
  .lesson-card h4 {
    margin: 0 0 5px 0;
    color: #0f172a;
    font-size: 11pt;
  }
  .lesson-card p {
    margin: 0;
    color: #334155;
    font-size: 10pt;
  }
  code {
    background: #e2e8f0;
    padding: 2px 5px;
    border-radius: 4px;
    font-family: ui-monospace, Menlo, Monaco, monospace;
    font-size: 9.5pt;
    color: #0f172a;
  }
  .badge {
    display: inline-block;
    background: #dbeafe;
    color: #1e40af;
    font-size: 8.5pt;
    font-weight: 600;
    padding: 2px 8px;
    border-radius: 12px;
    margin-bottom: 4px;
  }
  table {
    width: 100%;
    border-collapse: collapse;
    margin: 15px 0;
    font-size: 10pt;
  }
  th, td {
    border: 1px solid #cbd5e1;
    padding: 8px 10px;
    text-align: left;
  }
  th {
    background: #f1f5f9;
    color: #0f172a;
  }
</style>
</head>
<body>

<!-- COVER PAGE -->
<div class="cover">
  <div style="font-size: 36pt; margin-bottom: 10px;">🎓</div>
  <h1>EduTrainer Internship Complete Course Notes</h1>
  <h2>Technical Reference & Revision Guide (115 Lectures / 26 Modules)</h2>
  
  <div class="meta-box">
    <p><strong>Student Name:</strong> Nitishkumar Balappa Chimmanakatti</p>
    <p><strong>Internship Role:</strong> Web Development & Artificial Intelligence Intern</p>
    <p><strong>Training Portal:</strong> EduTrainer (internship.edutainer.in)</p>
    <p><strong>Affiliation:</strong> Visvesvaraya Technological University (VTU InternYet)</p>
    <p><strong>Completion Status:</strong> 100% Completed Across All Courses</p>
  </div>

  <div style="margin-top: 50px; text-align: left; max-width: 500px; margin-left: auto; margin-right: auto;">
    <h3 style="color: #475569; font-size: 11pt; text-transform: uppercase; letter-spacing: 1px;">Curriculum Scope</h3>
    <ul style="color: #334155; font-size: 10.5pt; line-height: 1.8;">
      <li><strong>Part 1:</strong> Full Stack Web Development Bootcamp (4 Modules / 32 Lectures)</li>
      <li><strong>Part 2:</strong> Python Essentials & Data Science Libraries (20 Modules / 67 Lectures)</li>
      <li><strong>Part 3:</strong> React JS Core & Component Architecture (2 Modules / 16 Lectures)</li>
    </ul>
  </div>
</div>

<!-- PART 1: FULL STACK WEB DEVELOPMENT BOOTCAMP -->
<h2 class="section-header">Part 1: Full Stack Web Development Bootcamp</h2>
<p style="color: #64748b; font-size: 10pt; margin-bottom: 20px;">Covers complete end-to-end web architecture from HTML5/CSS3 semantics to modern JavaScript ES6+, backend REST APIs with Node.js/Express, and full stack database persistence.</p>

<h3 class="module-header">Module 1: Frontend Foundations & Responsive Design (8 Lectures)</h3>
<div class="lesson-card">
  <span class="badge">Lecture 1</span>
  <h4>Web Architecture & HTTP Fundamentals</h4>
  <p>How the web works: Client-Server communication, DNS resolution, Request-Response lifecycle, HTTP verbs (<code>GET</code>, <code>POST</code>, <code>PUT</code>, <code>DELETE</code>), and status codes (200 OK, 404 Not Found, 500 Server Error).</p>
</div>
<div class="lesson-card">
  <span class="badge">Lecture 2</span>
  <h4>HTML5 Semantic Structure & Forms</h4>
  <p>Semantic tags (<code>&lt;header&gt;</code>, <code>&lt;main&gt;</code>, <code>&lt;section&gt;</code>, <code>&lt;article&gt;</code>, <code>&lt;footer&gt;</code>) for accessibility and SEO. Form elements, input types, attributes (<code>required</code>, <code>pattern</code>), and submission handling.</p>
</div>
<div class="lesson-card">
  <span class="badge">Lecture 3</span>
  <h4>CSS3 Styling & The Box Model</h4>
  <p>Understanding Content, Padding, Border, Margin, and <code>box-sizing: border-box</code>. Specificity hierarchy (inline &gt; ID &gt; class &gt; tag) and cascade inheritance rules.</p>
</div>
<div class="lesson-card">
  <span class="badge">Lecture 4</span>
  <h4>CSS Flexbox Layouts</h4>
  <p>One-dimensional flex layouts: <code>display: flex</code>, <code>flex-direction</code>, main-axis alignment (<code>justify-content</code>), cross-axis alignment (<code>align-items</code>), and wrapping behavior.</p>
</div>
<div class="lesson-card">
  <span class="badge">Lecture 5</span>
  <h4>CSS Grid Mastery</h4>
  <p>Two-dimensional grid layouts: <code>display: grid</code>, <code>grid-template-columns</code>, fractional units (<code>fr</code>), <code>grid-template-areas</code>, and auto-placement algorithms for dynamic dashboards.</p>
</div>
<div class="lesson-card">
  <span class="badge">Lecture 6</span>
  <h4>Responsive Web Design & Media Queries</h4>
  <p>Mobile-first responsive methodology using CSS media queries (<code>@media (min-width: 768px)</code>). Fluid units (<code>%</code>, <code>rem</code>, <code>vw</code>, <code>vh</code>) and responsive images.</p>
</div>
<div class="lesson-card">
  <span class="badge">Lecture 7</span>
  <h4>CSS Transitions & Keyframe Animations</h4>
  <p>Micro-interactions: <code>transition: all 0.3s ease</code>, hardware-accelerated transforms (<code>translate</code>, <code>scale</code>, <code>rotate</code>), and <code>@keyframes</code> for loading spinners and smooth UI state changes.</p>
</div>
<div class="lesson-card">
  <span class="badge">Lecture 8</span>
  <h4>Responsive Portfolio Project Build</h4>
  <p>Hands-on integration: Building an end-to-end responsive landing page combining semantic HTML5, Flexbox navigation, Grid portfolio items, and media query breakpoints.</p>
</div>

<h3 class="module-header">Module 2: Modern JavaScript (ES6+) & Client-Side Interactivity (8 Lectures)</h3>
<div class="lesson-card">
  <span class="badge">Lecture 9</span>
  <h4>JavaScript Basics & Scope Mechanics</h4>
  <p>Execution context, data types (primitives vs objects), <code>var</code> vs <code>let</code> vs <code>const</code>, block scoping, and variable hoisting.</p>
</div>
<div class="lesson-card">
  <span class="badge">Lecture 10</span>
  <h4>ES6 Features: Arrow Functions & Destructuring</h4>
  <p>Modern syntax: Concise arrow functions (<code>() =&gt; {}</code>), lexical <code>this</code> binding, array and object destructuring, and spread/rest operators (<code>...args</code>).</p>
</div>
<div class="lesson-card">
  <span class="badge">Lecture 11</span>
  <h4>DOM Selection & Manipulation</h4>
  <p>Accessing document nodes with <code>querySelector()</code> and <code>querySelectorAll()</code>. Dynamically modifying element text, inner HTML, CSS classes (<code>classList.add/toggle</code>), and styles.</p>
</div>
<div class="lesson-card">
  <span class="badge">Lecture 12</span>
  <h4>Event Handling & Delegation</h4>
  <p>Attaching listeners with <code>addEventListener()</code>. Event propagation mechanics: capturing, target, and bubbling phases. Event delegation for dynamically rendered items.</p>
</div>
<div class="lesson-card">
  <span class="badge">Lecture 13</span>
  <h4>Higher-Order Array Methods</h4>
  <p>Functional array transformations: <code>map()</code> (transformation), <code>filter()</code> (selection), <code>reduce()</code> (aggregation), <code>find()</code>, and <code>some()</code> for clean data processing.</p>
</div>
<div class="lesson-card">
  <span class="badge">Lecture 14</span>
  <h4>Asynchronous JavaScript & Event Loop</h4>
  <p>Single-threaded event loop, call stack, callback queue, microtask queue. Asynchronous flow with callbacks and Promises (<code>resolve</code>, <code>reject</code>, <code>.then()</code>, <code>.catch()</code>).</p>
</div>
<div class="lesson-card">
  <span class="badge">Lecture 15</span>
  <h4>Async / Await & Fetch API</h4>
  <p>Modern async handling using <code>async/await</code> with <code>try-catch</code>. Making HTTP requests with <code>fetch()</code>, parsing JSON payloads, and handling network errors.</p>
</div>
<div class="lesson-card">
  <span class="badge">Lecture 16</span>
  <h4>Interactive Frontend App (API Consumption)</h4>
  <p>Building a live data-fetching application (e.g. weather/crypto dashboard) with real-time search filtering, loading spinners, and dynamic DOM rendering.</p>
</div>

<h3 class="module-header">Module 3: Backend Development with Node.js & Express (8 Lectures)</h3>
<div class="lesson-card">
  <span class="badge">Lecture 17</span>
  <h4>Node.js Runtime & Architecture</h4>
  <p>V8 engine architecture, non-blocking asynchronous I/O, Node core modules (<code>fs</code>, <code>path</code>, <code>http</code>), and package management with <code>npm</code>.</p>
</div>
<div class="lesson-card">
  <span class="badge">Lecture 18</span>
  <h4>Express.js Framework & Server Setup</h4>
  <p>Initializing Express server instances, configuring port listeners, basic route handlers, and environment variable management using <code>dotenv</code>.</p>
</div>
<div class="lesson-card">
  <span class="badge">Lecture 19</span>
  <h4>Express Middleware Mechanics</h4>
  <p>Middleware execution pipeline (<code>(req, res, next) =&gt; {}</code>), built-in parsers (<code>express.json()</code>, <code>express.urlencoded()</code>), custom logging middleware, and CORS.</p>
</div>
<div class="lesson-card">
  <span class="badge">Lecture 20</span>
  <h4>RESTful API Design Principles</h4>
  <p>Stateless architecture, resource-oriented endpoint naming (<code>/api/items</code>), appropriate HTTP verbs, query parameters, route parameters (<code>req.params.id</code>), and standard response schemas.</p>
</div>
<div class="lesson-card">
  <span class="badge">Lecture 21</span>
  <h4>CRUD Operations Implementation</h4>
  <p>Building complete Create, Read, Update, Delete REST routes with proper status codes (201 Created, 200 OK, 204 No Content, 400 Bad Request, 404 Not Found).</p>
</div>
<div class="lesson-card">
  <span class="badge">Lecture 22</span>
  <h4>Centralized Error Handling in Express</h4>
  <p>Custom Application Error classes, catching async errors with wrappers, and global error-handling middleware (<code>(err, req, res, next) =&gt; {}</code>) returning consistent JSON errors.</p>
</div>
<div class="lesson-card">
  <span class="badge">Lecture 23</span>
  <h4>Input Validation & Data Sanitization</h4>
  <p>Validating incoming request payloads using libraries like <code>joi</code> or <code>express-validator</code>. Preventing malformed data and injection attacks before controller execution.</p>
</div>
<div class="lesson-card">
  <span class="badge">Lecture 24</span>
  <h4>Modular Express Router Architecture</h4>
  <p>Organizing production codebases using Express Routers (<code>express.Router()</code>), separating routes, controllers, and services into dedicated folders.</p>
</div>

<h3 class="module-header">Module 4: Database Integration & Production Deployment (8 Lectures)</h3>
<div class="lesson-card">
  <span class="badge">Lecture 25</span>
  <h4>Database Fundamentals: SQL vs NoSQL</h4>
  <p>Comparing relational schemas (tables, rows, foreign keys, ACID compliance) with document-based NoSQL collections (JSON documents, horizontal scalability).</p>
</div>
<div class="lesson-card">
  <span class="badge">Lecture 26</span>
  <h4>Database Connection & ODM / ORM Setup</h4>
  <p>Establishing persistent database connection pools (MongoDB/Mongoose or PostgreSQL/Sequelize) with connection retry logic and environment credentials.</p>
</div>
<div class="lesson-card">
  <span class="badge">Lecture 27</span>
  <h4>Schema Modeling & Validation Rules</h4>
  <p>Defining data models with strict schemas: field data types, required constraints, default values, timestamps, and custom schema validators.</p>
</div>
<div class="lesson-card">
  <span class="badge">Lecture 28</span>
  <h4>Database Querying & Pagination</h4>
  <p>Filtering, sorting, projecting specific fields, and implementing limit-skip pagination for high-volume data endpoints.</p>
</div>
<div class="lesson-card">
  <span class="badge">Lecture 29</span>
  <h4>Authentication & Password Hashing</h4>
  <p>Secure user authentication: Salting and hashing passwords with <code>bcrypt</code>, preventing plain-text credential leaks in database stores.</p>
</div>
<div class="lesson-card">
  <span class="badge">Lecture 30</span>
  <h4>JWT Token Authorization & Protected Routes</h4>
  <p>Stateless authorization using JSON Web Tokens (JWT). Generating signed tokens upon login and validating tokens in auth middleware via <code>Authorization: Bearer &lt;token&gt;</code>.</p>
</div>
<div class="lesson-card">
  <span class="badge">Lecture 31</span>
  <h4>Connecting Frontend to Backend API</h4>
  <p>Integrating client-side React/JavaScript forms with authenticated Express backend endpoints, managing auth tokens in browser storage, and CORS handling.</p>
</div>
<div class="lesson-card">
  <span class="badge">Lecture 32</span>
  <h4>Full Stack Deployment & Production Readiness</h4>
  <p>Production preparation: Environment variables, build bundling, security headers (<code>helmet</code>), rate limiting, and deploying frontend and backend to cloud providers (Render, Vercel, Netlify).</p>
</div>

<!-- PART 2: PYTHON ESSENTIALS AND LIBRARIES FOR DATA SCIENCE -->
<h2 class="section-header">Part 2: Python Essentials & Data Science Libraries</h2>
<p style="color: #64748b; font-size: 10pt; margin-bottom: 20px;">Comprehensive 20-module track covering Python syntax, data structures, OOP, file I/O, SQL connectivity, Tkinter GUIs, Django, NumPy vectorization, Pandas analytics, Matplotlib/Seaborn visualization, and Scikit-Learn workflows.</p>

<h3 class="module-header">Modules 1–4: Core Language, Control Flow & Functions (17 Lectures)</h3>
<div class="lesson-card">
  <span class="badge">Lessons 1–4</span>
  <h4>Python Syntax, Variables & Types</h4>
  <p>Interpreted execution, dynamic typing, arithmetic operators, string operations, and scalar types (<code>int</code>, <code>float</code>, <code>str</code>, <code>bool</code>).</p>
</div>
<div class="lesson-card">
  <span class="badge">Lessons 5–9</span>
  <h4>Decision Logic, Loops & Data Collections</h4>
  <p>Conditional branches (<code>if-elif-else</code>), <code>while</code> and <code>for</code> loops, indexed lists, immutable tuples, hash-map dictionaries, and unique sets.</p>
</div>
<div class="lesson-card">
  <span class="badge">Lessons 10–12</span>
  <h4>Loop Control & Advanced Collections</h4>
  <p><code>break</code> and <code>continue</code> statements, list comprehensions (<code>[x*2 for x in seq]</code>), dictionary comprehensions, and nested collection access.</p>
</div>
<div class="lesson-card">
  <span class="badge">Lessons 13–17</span>
  <h4>Modular Functions & Standard Library Utilities</h4>
  <p>Function signatures, return values, variable scope, built-in utilities (<code>zip</code>, <code>enumerate</code>), and functional programming (<code>map</code>, <code>filter</code>, <code>lambda</code>).</p>
</div>

<h3 class="module-header">Modules 5–8: Object-Oriented Design, I/O & Databases (13 Lectures)</h3>
<div class="lesson-card">
  <span class="badge">Lessons 18–23</span>
  <h4>OOP Principles: Classes, Inheritance & Polymorphism</h4>
  <p>Class declarations, instance state (<code>self</code>), constructor (<code>__init__</code>), encapsulation via naming conventions, single/multiple inheritance using <code>super()</code>, and polymorphic method overriding.</p>
</div>
<div class="lesson-card">
  <span class="badge">Lessons 24–26</span>
  <h4>Modules, Packages & Virtual Environments</h4>
  <p>Splitting code across files, package directory initialization (<code>__init__.py</code>), relative vs absolute imports, and package isolation using virtual environments.</p>
</div>
<div class="lesson-card">
  <span class="badge">Lessons 27–30</span>
  <h4>File Persistence & Database Connectivity</h4>
  <p>Safe file I/O with context managers (<code>with open()</code>), connecting to relational databases (SQLite/MySQL), executing CRUD queries with cursors, transactions (<code>commit/rollback</code>), and SQL injection prevention.</p>
</div>

<h3 class="module-header">Modules 9–12: GUI, Robustness & Django Web Framework (11 Lectures)</h3>
<div class="lesson-card">
  <span class="badge">Lessons 31–32</span>
  <h4>Desktop GUI with Tkinter</h4>
  <p>Root window lifecycle, layout managers (<code>pack</code>, <code>grid</code>), visual widgets (labels, buttons, text inputs), and event-driven button callback functions.</p>
</div>
<div class="lesson-card">
  <span class="badge">Lessons 33–34</span>
  <h4>Exception Handling & Custom Exceptions</h4>
  <p>Interception with <code>try-except</code>, clean recovery with <code>else</code>, guaranteed cleanup with <code>finally</code>, and defining custom domain exception classes inheriting from <code>Exception</code>.</p>
</div>
<div class="lesson-card">
  <span class="badge">Lessons 35–38</span>
  <h4>Advanced Python: Generators, Decorators & Threads</h4>
  <p>Variadic arguments (<code>*args</code>, <code>**kwargs</code>), memory-efficient generators (<code>yield</code>), function decorators (<code>@decorator</code>), and I/O concurrency with <code>threading.Thread</code>.</p>
</div>
<div class="lesson-card">
  <span class="badge">Lessons 39–41</span>
  <h4>Django Web Framework Fundamentals</h4>
  <p>Model-View-Template (MVT) architecture, URL routing dispatchers, view functions returning HTTP responses, and dynamic template rendering with context dictionaries.</p>
</div>

<h3 class="module-header">Modules 13–16: Numerical Computing & Data Visualization (10 Lectures)</h3>
<div class="lesson-card">
  <span class="badge">Lessons 42–44</span>
  <h4>NumPy Vectorization & N-Dimensional Arrays</h4>
  <p>Homogeneous <code>ndarray</code> objects, slicing multi-dimensional arrays, vectorized arithmetic eliminating slow Python loops, broadcasting rules, and aggregation functions (<code>np.mean</code>, <code>np.sum</code>, <code>np.std</code>).</p>
</div>
<div class="lesson-card">
  <span class="badge">Lessons 45–47</span>
  <h4>Pandas Data Wrangling & Analytics</h4>
  <p>Series and DataFrames, reading CSV datasets (<code>pd.read_csv</code>), positional/label indexing (<code>iloc</code>/<code>loc</code>), handling missing values (<code>dropna</code>/<code>fillna</code>), and grouped aggregations (<code>groupby</code>).</p>
</div>
<div class="lesson-card">
  <span class="badge">Lessons 48–51</span>
  <h4>Matplotlib & Seaborn Visualizations</h4>
  <p>Plotting line charts, bar plots, histograms, and scatter plots using Matplotlib. Creating high-level statistical visuals, distribution plots (KDE), and correlation heatmaps with Seaborn.</p>
</div>

<h3 class="module-header">Modules 17–20: Data Wrangling, Scikit-Learn & Projects (16 Lectures)</h3>
<div class="lesson-card">
  <span class="badge">Lessons 52–54</span>
  <h4>Data Wrangling & Scikit-Learn Introduction</h4>
  <p>End-to-end data preparation: outlier detection, feature encoding, feature scaling (StandardScaler, MinMaxScaler), and Scikit-Learn's Estimator API (<code>fit</code>, <code>transform</code>, <code>predict</code>).</p>
</div>
<div class="lesson-card">
  <span class="badge">Lessons 55–57</span>
  <h4>Graphics & Integrated Python Applications</h4>
  <p>Turtle graphics coordinate drawings, modular software organization, and building integrated utility programs combining file storage with business logic.</p>
</div>
<div class="lesson-card">
  <span class="badge">Lessons 58–61</span>
  <h4>Algorithmic Challenges & Regular Expressions</h4>
  <p>Algorithm optimization, Big-O complexity awareness, and regular expressions with the <code>re</code> module (pattern matching, validation, extraction).</p>
</div>
<div class="lesson-card">
  <span class="badge">Lessons 62–67</span>
  <h4>Data Science Capstone Mini-Projects</h4>
  <p>Six hands-on applied projects: CLI analysis utility, automated cleaning pipeline, exploratory data analysis dashboard, feature engineering workflow, baseline predictive model, and full data pipeline.</p>
</div>

<!-- PART 3: REACT JS CORE & COMPONENT ARCHITECTURE -->
<h2 class="section-header">Part 3: React JS Core & Component Architecture</h2>
<p style="color: #64748b; font-size: 10pt; margin-bottom: 20px;">Modern component-based frontend development covering Single Page Applications (SPA), Virtual DOM, JSX, Hooks (<code>useState</code>, <code>useEffect</code>, <code>useContext</code>), Forms, Routing, and Production Deployment.</p>

<h3 class="module-header">Module 1: React Fundamentals & Component Architecture (8 Lectures)</h3>
<div class="lesson-card">
  <span class="badge">Lecture 1</span>
  <h4>Single Page Applications (SPA) & Virtual DOM</h4>
  <p>Why React: Eliminating full-page browser reloads. How the Virtual DOM uses a diffing algorithm (Reconciliation) to selectively update only changed nodes in the real DOM for high performance.</p>
</div>
<div class="lesson-card">
  <span class="badge">Lecture 2</span>
  <h4>Project Setup: Vite / Create-React-App</h4>
  <p>Scaffolding modern React applications, understanding folder structure (<code>src</code>, <code>public</code>, <code>package.json</code>), bundler mechanisms, and Hot Module Replacement (HMR).</p>
</div>
<div class="lesson-card">
  <span class="badge">Lecture 3</span>
  <h4>JSX Syntax & Rendering Logic</h4>
  <p>JavaScript XML syntax rules: Single parent wrapper element, self-closing tags, <code>className</code> instead of <code>class</code>, and embedding dynamic JavaScript expressions using curly braces <code>{expression}</code>.</p>
</div>
<div class="lesson-card">
  <span class="badge">Lecture 4</span>
  <h4>Functional Components & Props</h4>
  <p>Declaring pure functional components. Passing data unidirectionally from parent to child via <code>props</code> (read-only), prop destructuring, and default prop values.</p>
</div>
<div class="lesson-card">
  <span class="badge">Lecture 5</span>
  <h4>State Management with <code>useState</code> Hook</h4>
  <p>Managing dynamic component state. Rules of Hooks, state immutability, updater functions (<code>setCount(prev =&gt; prev + 1)</code>), and re-render triggers.</p>
</div>
<div class="lesson-card">
  <span class="badge">Lecture 6</span>
  <h4>Lifecycle & Side Effects with <code>useEffect</code></h4>
  <p>Handling side effects (data fetching, DOM listeners, timers). Dependency array semantics: no array (every render), empty array <code>[]</code> (mount only), dependency values <code>[id]</code>, and cleanup functions.</p>
</div>
<div class="lesson-card">
  <span class="badge">Lecture 7</span>
  <h4>Conditional Rendering Techniques</h4>
  <p>Rendering dynamic UI elements conditionally using ternary operators (<code>condition ? &lt;A/&gt; : &lt;B/&gt;</code>), short-circuit evaluation (<code>loading &amp;&amp; &lt;Spinner/&gt;</code>), and early returns.</p>
</div>
<div class="lesson-card">
  <span class="badge">Lecture 8</span>
  <h4>List Rendering & Key Attribute Rules</h4>
  <p>Iterating over data arrays using <code>.map()</code> to render component lists. Importance of stable, unique <code>key</code> attributes for efficient Virtual DOM reconciliation.</p>
</div>

<h3 class="module-header">Module 2: Advanced React, Global State & Routing (8 Lectures)</h3>
<div class="lesson-card">
  <span class="badge">Lecture 9</span>
  <h4>Controlled Forms & Two-Way Data Binding</h4>
  <p>Handling form input state in React: Binding <code>value={formData.email}</code> and listening to <code>onChange</code> events. Preventing default submission with <code>e.preventDefault()</code>.</p>
</div>
<div class="lesson-card">
  <span class="badge">Lecture 10</span>
  <h4>Form Validation & Error States</h4>
  <p>Client-side form validation patterns: Tracking touched inputs, displaying real-time validation error banners, and disabling submit buttons until form schemas are valid.</p>
</div>
<div class="lesson-card">
  <span class="badge">Lecture 11</span>
  <h4>Lifting State Up & Component Composition</h4>
  <p>Sharing state between sibling components by moving state to their common ancestor and passing callback functions as props. Building compound component layouts.</p>
</div>
<div class="lesson-card">
  <span class="badge">Lecture 12</span>
  <h4>Context API for Global State Management</h4>
  <p>Solving prop-drilling across deeply nested components. Creating contexts (<code>createContext</code>), wrapping trees with <code>Provider</code>, and consuming global values with <code>useContext</code>.</p>
</div>
<div class="lesson-card">
  <span class="badge">Lecture 13</span>
  <h4>Client-Side Routing with React Router</h4>
  <p>Configuring browser navigation using <code>BrowserRouter</code>, <code>Routes</code>, and <code>Route</code>. Navigation without page reload via <code>&lt;Link&gt;</code> and programmatic navigation with <code>useNavigate()</code>.</p>
</div>
<div class="lesson-card">
  <span class="badge">Lecture 14</span>
  <h4>Dynamic Route Parameters & Nested Layouts</h4>
  <p>Extracting dynamic URL parameters using <code>useParams()</code> (e.g. <code>/products/:id</code>), query string handling with <code>useSearchParams()</code>, and shared parent layouts using <code>&lt;Outlet/&gt;</code>.</p>
</div>
<div class="lesson-card">
  <span class="badge">Lecture 15</span>
  <h4>Performance Optimization (<code>useMemo</code> &amp; <code>useCallback</code>)</h4>
  <p>Preventing unnecessary recalculations using <code>useMemo()</code> for expensive computations and memoizing callback references with <code>useCallback()</code> to stop unwanted child re-renders.</p>
</div>
<div class="lesson-card">
  <span class="badge">Lecture 16</span>
  <h4>Production Build & Cloud Deployment</h4>
  <p>Optimizing React applications for production: Tree-shaking, code-splitting with <code>React.lazy</code> and <code>Suspense</code>, asset minification (<code>npm run build</code>), and deploying to Vercel/Netlify.</p>
</div>

</body>
</html>
"""


def main():
    out_dir = Path("/Users/nitishkumarbchimmanakatti/.gemini/antigravity/brain/6ce00d1c-03b2-4d6c-872c-f49c65c23f32")
    pdf_path = out_dir / "EduTrainer_Complete_Internship_Course_Notes.pdf"
    html_path = out_dir / "EduTrainer_Complete_Internship_Course_Notes.html"

    # Save HTML
    html_path.write_text(HTML_CONTENT, encoding="utf-8")
    print(f"Saved HTML source to {html_path}")

    # Generate high-quality PDF using Playwright
    print("Generating publication-quality PDF via Playwright...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_content(HTML_CONTENT, wait_until="networkidle")
        page.pdf(
            path=str(pdf_path),
            format="A4",
            print_background=True,
            margin={"top": "20mm", "bottom": "20mm", "left": "15mm", "right": "15mm"}
        )
        browser.close()

    print(f"✅ Generated PDF successfully: {pdf_path} ({pdf_path.stat().st_size} bytes)")

    # Send document directly to student's Telegram Bot
    print("Sending PDF to user's Telegram bot...")
    caption = (
        "📚 EduTrainer Complete Course Notes (PDF)\n"
        "👤 Student: Nitishkumar Balappa Chimmanakatti\n"
        "🎓 Courses Covered:\n"
        "  1. Full Stack Web Development Bootcamp (32 Lectures)\n"
        "  2. Python Essentials & Data Science (67 Lectures)\n"
        "  3. React JS Component Architecture (16 Lectures)\n"
        "📖 Total: 115 Lectures / 26 Modules"
    )
    res, msg = send_telegram_document(pdf_path, caption=caption)
    print(f"Telegram Delivery Result: {res} | {msg}")


if __name__ == "__main__":
    main()
