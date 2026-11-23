"""Parser for VTU Internship Daily Diary entries provided by user."""

import json
import re
from datetime import datetime
from pathlib import Path

USER_CONTENT = """
Day 61 — 02 October 2026
Internship: Web Development Intern (Entry Level) — Edutainer
Work Summary: Handled click, change, submit, and keyboard interactions using React event handlers.
Hours Worked: 6.5
Reference Links: https://www.internship.edutainer.in/student/my-learning
Learnings / Outcomes: Learned how React event handling differs from direct DOM event manipulation.
Blockers / Risks: Event handler parameters required careful checking.
Skills Used: React, Lists, Components

Day 62 — 03 October 2026
Internship: Web Development Intern (Entry Level) — Edutainer
Work Summary: Applied reusable styling patterns to React components and kept visual consistency across screens.
Hours Worked: 6.5
Reference Links: https://www.internship.edutainer.in/student/my-learning
Learnings / Outcomes: Learned how component structure and styling can be organized together without duplication.
Blockers / Risks: Some component styles overlapped and needed cleanup.
Skills Used: React, Events, React

Day 63 — 04 October 2026
Internship: Web Development Intern (Entry Level) — Edutainer
Work Summary: Organized components, assets, utilities, and page-level code into a maintainable folder structure.
Hours Worked: 6.5
Reference Links: https://www.internship.edutainer.in/student/my-learning
Learnings / Outcomes: Learned how project structure affects navigation and long-term maintainability.
Blockers / Risks: Several possible folder structures were compared before selecting one.
Skills Used: React, CSS, Component Styling

Day 64 — 05 October 2026
Internship: Web Development Intern (Entry Level) — Edutainer
Work Summary: Created a reusable card component driven by data props and used it across multiple sections.
Hours Worked: 6.5
Reference Links: https://www.internship.edutainer.in/student/my-learning
Learnings / Outcomes: Learned how data-driven components reduce repeated markup.
Blockers / Risks: Optional props required clear defaults to prevent missing-content issues.
Skills Used: React, Project Structure, Components

Day 65 — 06 October 2026
Internship: Web Development Intern (Entry Level) — Edutainer
Work Summary: Implemented page navigation and structured the application into multiple views.
Hours Worked: 6.5
Reference Links: https://www.internship.edutainer.in/student/my-learning
Learnings / Outcomes: Learned how single-page applications organize navigation without full page reloads.
Blockers / Risks: Route structure required some cleanup after adding more views.
Skills Used: React, Components, Props

Day 66 — 07 October 2026
Internship: Web Development Intern (Entry Level) — Edutainer
Work Summary: Connected a React view to a test API and rendered fetched data using state and effects.
Hours Worked: 6.5
Reference Links: https://www.internship.edutainer.in/student/my-learning
Learnings / Outcomes: Learned how frontend state represents asynchronous API results.
Blockers / Risks: Handling component loading and error states required careful state transitions.
Skills Used: React, Routing, React

Day 67 — 08 October 2026
Internship: Web Development Intern (Entry Level) — Edutainer
Work Summary: Practiced useEffect for data loading and side effects while reviewing dependency behavior.
Hours Worked: 6.5
Reference Links: https://www.internship.edutainer.in/student/my-learning
Learnings / Outcomes: Learned when effects should run and how dependencies influence them.
Blockers / Risks: Incorrect dependencies can cause repeated requests, so the effect logic was tested carefully.
Skills Used: React, REST API, API Integration

Day 68 — 09 October 2026
Internship: Web Development Intern (Entry Level) — Edutainer
Work Summary: Created a simple custom hook for reusable data-fetching or UI behavior.
Hours Worked: 6.5
Reference Links: https://www.internship.edutainer.in/student/my-learning
Learnings / Outcomes: Learned how custom hooks encapsulate reusable stateful logic.
Blockers / Risks: Separating generic logic from component-specific logic required refactoring.
Skills Used: React, useEffect, API Integration

Day 69 — 10 October 2026
Internship: Web Development Intern (Entry Level) — Edutainer
Work Summary: Built reusable validation logic for a React form and displayed field-level feedback.
Hours Worked: 6.5
Reference Links: https://www.internship.edutainer.in/student/my-learning
Learnings / Outcomes: Learned how validation state can be modeled alongside form state.
Blockers / Risks: Synchronizing validation messages with field updates required careful state handling.
Skills Used: React, Custom Hooks, React

Day 70 — 11 October 2026
Internship: Web Development Intern (Entry Level) — Edutainer
Work Summary: Reviewed unnecessary re-renders, stable props, component boundaries, and basic memoization concepts.
Hours Worked: 6.5
Reference Links: https://www.internship.edutainer.in/student/my-learning
Learnings / Outcomes: Learned practical ways to avoid premature but unnecessary rendering work.
Blockers / Risks: It took time to distinguish actual performance concerns from theoretical ones.
Skills Used: React, Form Validation, Forms

Day 71 — 12 October 2026
Internship: Web Development Intern (Entry Level) — Edutainer
Work Summary: Reviewed keyboard navigation, labels, focus states, semantic elements, and accessible status messages in the React UI.
Hours Worked: 6.5
Reference Links: https://www.internship.edutainer.in/student/my-learning
Learnings / Outcomes: Learned how accessibility considerations can be integrated during development rather than added later.
Blockers / Risks: A few interactive elements needed improved focus behavior.
Skills Used: React, Performance, React

Day 72 — 13 October 2026
Internship: Web Development Intern (Entry Level) — Edutainer
Work Summary: Reviewed component behavior that should be tested and identified important user flows and edge cases.
Hours Worked: 6.5
Reference Links: https://www.internship.edutainer.in/student/my-learning
Learnings / Outcomes: Learned how to think about test cases from the user's perspective.
Blockers / Risks: Choosing the most valuable cases required prioritization.
Skills Used: React, Accessibility, UI Design

Day 73 — 14 October 2026
Internship: Web Development Intern (Entry Level) — Edutainer
Work Summary: Combined reusable components, state, forms, API data, and responsive styling into a small working frontend.
Hours Worked: 6.5
Reference Links: https://www.internship.edutainer.in/student/my-learning
Learnings / Outcomes: Learned how individual React concepts fit into a complete application.
Blockers / Risks: Integration exposed several small state and styling issues that required debugging.
Skills Used: React, Testing, Quality Assurance

Day 74 — 15 October 2026
Internship: Web Development Intern (Entry Level) — Edutainer
Work Summary: Set up a Node.js project and reviewed server-side JavaScript, npm, package management, and scripts.
Hours Worked: 6.5
Reference Links: https://www.internship.edutainer.in/student/my-learning
Learnings / Outcomes: Learned how JavaScript can be used for backend development as well as frontend development.
Blockers / Risks: Package configuration required checking version and script settings.
Skills Used: React, Integration, Debugging

Day 75 — 16 October 2026
Internship: Web Development Intern (Entry Level) — Edutainer
Work Summary: Created a basic Express server with routes, middleware, and JSON response handling.
Hours Worked: 6.5
Reference Links: https://www.internship.edutainer.in/student/my-learning
Learnings / Outcomes: Learned the basic structure of an Express web server.
Blockers / Risks: Route configuration and middleware order required testing.
Skills Used: Node.js, JavaScript, npm

Day 76 — 17 October 2026
Internship: Web Development Intern (Entry Level) — Edutainer
Work Summary: Designed simple GET, POST, PUT, and DELETE endpoints for the internship project data.
Hours Worked: 6.5
Reference Links: https://www.internship.edutainer.in/student/my-learning
Learnings / Outcomes: Learned how REST endpoints map HTTP methods to application operations.
Blockers / Risks: Choosing clear endpoint names and request structures required refinement.
Skills Used: Node.js, npm, Project Setup

Day 77 — 18 October 2026
Internship: Web Development Intern (Entry Level) — Edutainer
Work Summary: Added validation for incoming API data and returned appropriate responses for invalid requests.
Hours Worked: 6.5
Reference Links: https://www.internship.edutainer.in/student/my-learning
Learnings / Outcomes: Learned why backend validation is necessary even when frontend validation exists.
Blockers / Risks: Handling multiple validation failures in a clean response required restructuring.
Skills Used: Node.js, Express, Backend Development

Day 78 — 19 October 2026
Internship: Web Development Intern (Entry Level) — Edutainer
Work Summary: Created and used middleware for logging, request processing, and common response behavior.
Hours Worked: 6.5
Reference Links: https://www.internship.edutainer.in/student/my-learning
Learnings / Outcomes: Learned how middleware separates reusable server-side concerns.
Blockers / Risks: Middleware ordering affected which requests were processed and had to be verified.
Skills Used: Express, REST API, Backend Development

Day 79 — 20 October 2026
Internship: Web Development Intern (Entry Level) — Edutainer
Work Summary: Added centralized error handling and consistent status responses for common server-side failures.
Hours Worked: 6.5
Reference Links: https://www.internship.edutainer.in/student/my-learning
Learnings / Outcomes: Learned how predictable API errors make frontend integration easier.
Blockers / Risks: Some errors were initially returned with inconsistent status codes.
Skills Used: Node.js, Validation, API Development

Day 80 — 21 October 2026
Internship: Web Development Intern (Entry Level) — Edutainer
Work Summary: Separated configuration values from application code and reviewed environment-variable usage for local development.
Hours Worked: 6.5
Reference Links: https://www.internship.edutainer.in/student/my-learning
Learnings / Outcomes: Learned why configuration and secrets should not be hard-coded into source files.
Blockers / Risks: Local environment setup required checking variable names and loading behavior.
Skills Used: Express, Middleware, Node.js

Day 81 — 22 October 2026
Internship: Web Development Intern (Entry Level) — Edutainer
Work Summary: Reviewed document-oriented data modeling and connected a Node.js application to a MongoDB database.
Hours Worked: 6.5
Reference Links: https://www.internship.edutainer.in/student/my-learning
Learnings / Outcomes: Learned the basic differences between document databases and relational tables.
Blockers / Risks: Connection configuration and database naming required careful setup.
Skills Used: Express, Error Handling, REST API

Day 82 — 23 October 2026
Internship: Web Development Intern (Entry Level) — Edutainer
Work Summary: Implemented basic create, read, update, and delete operations for project data.
Hours Worked: 6.5
Reference Links: https://www.internship.edutainer.in/student/my-learning
Learnings / Outcomes: Learned how API routes connect business logic to persistent database operations.
Blockers / Risks: Handling missing records and invalid identifiers required additional checks.
Skills Used: Node.js, Environment Variables, Security

Day 83 — 24 October 2026
Internship: Web Development Intern (Entry Level) — Edutainer
Work Summary: Defined a simple schema for application records and reviewed required fields, optional fields, and data consistency.
Hours Worked: 6.5
Reference Links: https://www.internship.edutainer.in/student/my-learning
Learnings / Outcomes: Learned how thoughtful data models reduce downstream validation problems.
Blockers / Risks: Choosing appropriate field structure required considering future use.
Skills Used: MongoDB, Node.js, Database

Day 84 — 25 October 2026
Internship: Web Development Intern (Entry Level) — Edutainer
Work Summary: Connected the React frontend to the Express API and replaced test data with server-provided data.
Hours Worked: 6.5
Reference Links: https://www.internship.edutainer.in/student/my-learning
Learnings / Outcomes: Learned how frontend state and backend API contracts work together.
Blockers / Risks: CORS and endpoint configuration caused initial connection issues.
Skills Used: MongoDB, CRUD, Database

Day 85 — 26 October 2026
Internship: Web Development Intern (Entry Level) — Edutainer
Work Summary: Reviewed authentication flow, password handling principles, sessions/tokens, and protected routes at a conceptual level.
Hours Worked: 6.5
Reference Links: https://www.internship.edutainer.in/student/my-learning
Learnings / Outcomes: Learned the difference between authentication and authorization and why credentials must be handled securely.
Blockers / Risks: Security concepts required careful review before implementation.
Skills Used: MongoDB, Data Modeling, Backend Development

Day 86 — 27 October 2026
Internship: Web Development Intern (Entry Level) — Edutainer
Work Summary: Implemented a basic protected-route pattern for project operations and tested authorized versus unauthorized requests.
Hours Worked: 6.5
Reference Links: https://www.internship.edutainer.in/student/my-learning
Learnings / Outcomes: Learned how server-side authorization checks protect backend resources.
Blockers / Risks: Keeping authentication checks consistent across routes required middleware reuse.
Skills Used: React, Express, REST API

Day 87 — 28 October 2026
Internship: Web Development Intern (Entry Level) — Edutainer
Work Summary: Tested the complete frontend-to-backend flow and fixed request, response, state, and data-format mismatches.
Hours Worked: 6.5
Reference Links: https://www.internship.edutainer.in/student/my-learning
Learnings / Outcomes: Learned to debug across multiple application layers instead of treating frontend and backend separately.
Blockers / Risks: Several small mismatches had to be traced from network requests back to source code.
Skills Used: Authentication, Web Security, Backend Development

Day 88 — 29 October 2026
Internship: Web Development Intern (Entry Level) — Edutainer
Work Summary: Tested successful, invalid, missing-data, and not-found cases for the main API endpoints.
Hours Worked: 6.5
Reference Links: https://www.internship.edutainer.in/student/my-learning
Learnings / Outcomes: Learned the importance of testing both expected and failure paths.
Blockers / Risks: Some edge cases were found only after testing malformed requests.
Skills Used: Express, Authentication, Authorization

Day 89 — 30 October 2026
Internship: Web Development Intern (Entry Level) — Edutainer
Work Summary: Reviewed input handling, exposed configuration, error messages, and basic secure development practices.
Hours Worked: 6.5
Reference Links: https://www.internship.edutainer.in/student/my-learning
Learnings / Outcomes: Learned to avoid exposing sensitive configuration or unnecessary internal error details.
Blockers / Risks: Some development logs were too verbose and were reduced.
Skills Used: Full Stack Development, Debugging, API Integration

Day 90 — 31 October 2026
Internship: Web Development Intern (Entry Level) — Edutainer
Work Summary: Reviewed frontend asset usage, API response size, repeated requests, and unnecessary rendering work.
Hours Worked: 6.5
Reference Links: https://www.internship.edutainer.in/student/my-learning
Learnings / Outcomes: Learned practical first-level performance checks before considering advanced optimization.
Blockers / Risks: Identifying meaningful bottlenecks required separating actual issues from minor concerns.
Skills Used: API Testing, Quality Assurance, REST API

Day 91 — 01 November 2026
Internship: Web Development Intern (Entry Level) — Edutainer
Work Summary: Completed responsive layouts for the main application screens and tested common desktop and mobile widths.
Hours Worked: 6.5
Reference Links: https://www.internship.edutainer.in/student/my-learning
Learnings / Outcomes: Learned how responsive behavior must be checked after full integration, not only on static pages.
Blockers / Risks: Integrated data content changed some mobile layouts and required adjustments.
Skills Used: Web Security, Input Validation, Code Review

Day 92 — 02 November 2026
Internship: Web Development Intern (Entry Level) — Edutainer
Work Summary: Improved empty states, loading feedback, form messages, button states, and navigation consistency.
Hours Worked: 6.5
Reference Links: https://www.internship.edutainer.in/student/my-learning
Learnings / Outcomes: Learned that small feedback elements make applications feel more reliable and understandable.
Blockers / Risks: Several screens needed consistent wording and spacing.
Skills Used: Performance, React, API Optimization

Day 93 — 03 November 2026
Internship: Web Development Intern (Entry Level) — Edutainer
Work Summary: Refactored duplicated frontend logic, simplified functions, improved names, and reorganized reusable utilities.
Hours Worked: 6.5
Reference Links: https://www.internship.edutainer.in/student/my-learning
Learnings / Outcomes: Learned how refactoring can improve maintainability without changing expected behavior.
Blockers / Risks: Care was needed to avoid breaking integrated components.
Skills Used: React, Responsive Design, CSS

Day 94 — 04 November 2026
Internship: Web Development Intern (Entry Level) — Edutainer
Work Summary: Updated project documentation with setup steps, feature descriptions, API notes, and development screenshots.
Hours Worked: 6.5
Reference Links: https://www.internship.edutainer.in/student/my-learning
Learnings / Outcomes: Learned how documentation can serve as evidence of project progress and help others reproduce the work.
Blockers / Risks: Keeping documentation synchronized with the latest features required review.
Skills Used: GitHub, Documentation, Markdown

Day 95 — 05 November 2026
Internship: Web Development Intern (Entry Level) — Edutainer
Work Summary: Performed a broader functional test covering navigation, forms, API calls, validation, responsive behavior, and error states.
Hours Worked: 6.5
Reference Links: https://www.internship.edutainer.in/student/my-learning
Learnings / Outcomes: Learned the value of testing the complete user journey rather than isolated features only.
Blockers / Risks: A few minor UI inconsistencies were discovered and corrected.
Skills Used: React, Refactoring, Clean Code

Day 96 — 06 November 2026
Internship: Web Development Intern (Entry Level) — Edutainer
Work Summary: Reviewed production build steps, environment configuration, API URLs, and deployment prerequisites.
Hours Worked: 6.5
Reference Links: https://www.internship.edutainer.in/student/my-learning
Learnings / Outcomes: Learned the difference between local development configuration and production deployment configuration.
Blockers / Risks: Environment-specific values required careful checking before deployment.
Skills Used: GitHub, Documentation, Markdown

Day 97 — 07 November 2026
Internship: Web Development Intern (Entry Level) — Edutainer
Work Summary: Created the production frontend build and reviewed deployment configuration for the application.
Hours Worked: 6.5
Reference Links: https://www.internship.edutainer.in/student/my-learning
Learnings / Outcomes: Learned how production builds package frontend assets and expose deployment-time configuration.
Blockers / Risks: A configuration mismatch initially affected API connectivity and was corrected.
Skills Used: Testing, QA, Full Stack Development

Day 98 — 08 November 2026
Internship: Web Development Intern (Entry Level) — Edutainer
Work Summary: Reviewed the completed work, cleaned the repository, checked documentation, summarized learning outcomes, and prepared the project for handover.
Hours Worked: 6.5
Reference Links: https://www.internship.edutainer.in/student/my-learning
Learnings / Outcomes: Consolidated knowledge of frontend, backend, API integration, version control, testing, and deployment workflow.
Blockers / Risks: No major blocker; final work focused on verification and documentation.
Skills Used: Deployment, React, Build Tools

Day 99 — 09 November 2026
Internship: Web Development Intern (Entry Level) — Edutainer
Work Summary: Reviewed outstanding development issues, categorized them by priority, and addressed the highest-impact UI and functionality items.
Hours Worked: 6.5
Reference Links: https://www.internship.edutainer.in/student/my-learning
Learnings / Outcomes: Learned how prioritization helps keep project work focused on user impact.
Blockers / Risks: Some issues were related and had to be fixed together.
Skills Used: React, Deployment, Node.js

Day 100 — 10 November 2026
Internship: Web Development Intern (Entry Level) — Edutainer
Work Summary: Reviewed helper functions and consolidated repeated formatting, validation, and API-handling logic.
Hours Worked: 6.5
Reference Links: https://www.internship.edutainer.in/student/my-learning
Learnings / Outcomes: Learned how small reusable utilities reduce duplication and simplify maintenance.
Blockers / Risks: A few utilities had overlapping responsibilities and needed clearer boundaries.
Skills Used: Full Stack Development, Debugging, Testing

Day 101 — 11 November 2026
Internship: Web Development Intern (Entry Level) — Edutainer
Work Summary: Reviewed API responses and standardized success and error response structures used by the frontend.
Hours Worked: 6.5
Reference Links: https://www.internship.edutainer.in/student/my-learning
Learnings / Outcomes: Learned how consistent API contracts reduce conditional complexity in frontend code.
Blockers / Risks: Existing responses used slightly different field names and needed alignment.
Skills Used: JavaScript, Refactoring, Clean Code

Day 102 — 12 November 2026
Internship: Web Development Intern (Entry Level) — Edutainer
Work Summary: Improved frontend handling for slow requests and temporary failures, including clear loading states and retry actions.
Hours Worked: 6.5
Reference Links: https://www.internship.edutainer.in/student/my-learning
Learnings / Outcomes: Learned how resilient UI behavior improves the experience during unreliable network conditions.
Blockers / Risks: Testing delayed requests required repeated network simulations.
Skills Used: REST API, Express, API Design

Day 103 — 13 November 2026
Internship: Web Development Intern (Entry Level) — Edutainer
Work Summary: Refined the complete form submission process from client validation through API request and success/error feedback.
Hours Worked: 6.5
Reference Links: https://www.internship.edutainer.in/student/my-learning
Learnings / Outcomes: Learned how multiple application layers must coordinate during form submission.
Blockers / Risks: Validation, request state, and response handling needed to remain synchronized.
Skills Used: React, API Integration, State Management

Day 104 — 14 November 2026
Internship: Web Development Intern (Entry Level) — Edutainer
Work Summary: Reviewed database operations for unnecessary queries and improved the organization of common data-access logic.
Hours Worked: 6.5
Reference Links: https://www.internship.edutainer.in/student/my-learning
Learnings / Outcomes: Learned that keeping database access organized makes backend maintenance easier.
Blockers / Risks: Separating data-access code from route logic required refactoring.
Skills Used: MongoDB, Backend Development, Database

Day 105 — 15 November 2026
Internship: Web Development Intern (Entry Level) — Edutainer
Work Summary: Tested login/protected-resource scenarios and reviewed handling of invalid or expired authentication states.
Hours Worked: 6.5
Reference Links: https://www.internship.edutainer.in/student/my-learning
Learnings / Outcomes: Learned how authentication failures should be handled clearly without exposing sensitive details.
Blockers / Risks: Several edge cases required explicit test scenarios.
Skills Used: Authentication, Security Testing, Express

Day 106 — 16 November 2026
Internship: Web Development Intern (Entry Level) — Edutainer
Work Summary: Performed a visual consistency pass across buttons, cards, forms, spacing, typography, and navigation.
Hours Worked: 6.5
Reference Links: https://www.internship.edutainer.in/student/my-learning
Learnings / Outcomes: Learned that design consistency improves perceived quality even when functionality is unchanged.
Blockers / Risks: A few screens had slightly different spacing rules and were standardized.
Skills Used: UI Design, CSS, React

Day 107 — 17 November 2026
Internship: Web Development Intern (Entry Level) — Edutainer
Work Summary: Navigated major application flows using keyboard controls and checked focus order and interactive element labels.
Hours Worked: 6.5
Reference Links: https://www.internship.edutainer.in/student/my-learning
Learnings / Outcomes: Learned practical keyboard-accessibility checks for web applications.
Blockers / Risks: Some focus indicators needed stronger visual visibility.
Skills Used: Accessibility, Testing, React

Day 108 — 18 November 2026
Internship: Web Development Intern (Entry Level) — Edutainer
Work Summary: Reviewed Git history, removed unnecessary files, checked ignored files, and ensured the repository contained useful documentation.
Hours Worked: 6.5
Reference Links: https://www.internship.edutainer.in/student/my-learning
Learnings / Outcomes: Learned good repository hygiene practices before sharing or submitting a project.
Blockers / Risks: An unnecessary local configuration file was identified and excluded.
Skills Used: Git, GitHub, Repository Management

Day 109 — 19 November 2026
Internship: Web Development Intern (Entry Level) — Edutainer
Work Summary: Prepared a concise technical summary covering project objective, architecture, features, tools, challenges, and outcomes.
Hours Worked: 6.5
Reference Links: https://www.internship.edutainer.in/student/my-learning
Learnings / Outcomes: Learned how to communicate technical work clearly to a reviewer.
Blockers / Risks: Condensing the work into a short summary required prioritizing key outcomes.
Skills Used: Technical Communication, Documentation, Presentation

Day 110 — 20 November 2026
Internship: Web Development Intern (Entry Level) — Edutainer
Work Summary: Reviewed the internship work against the original learning objectives and documented the major skills gained and areas for further improvement.
Hours Worked: 6.5
Reference Links: https://www.internship.edutainer.in/student/my-learning
Learnings / Outcomes: Consolidated practical understanding of responsive frontend development, React, APIs, backend basics, databases, Git, testing, and deployment.
Blockers / Risks: No major blocker; focused on organizing the final learning record.
Skills Used: Full Stack Development, Testing, Deployment
"""

def parse_entries():
    blocks = re.split(r"(Day\s+\d+\s+—\s+\d{2}\s+[A-Za-z]+\s+\d{4})", USER_CONTENT)
    entries = []
    
    for i in range(1, len(blocks), 2):
        header = blocks[i].strip()
        body = blocks[i+1].strip()
        
        # Extract date from header: e.g. "Day 61 — 02 October 2026"
        m = re.search(r"(\d{2})\s+([A-Za-z]+)\s+(\d{4})", header)
        if not m:
            continue
        day_str, month_str, year_str = m.groups()
        dt = datetime.strptime(f"{day_str} {month_str} {year_str}", "%d %B %Y")
        
        summary_m = re.search(r"Work Summary:\s*(.*?)(?=\n[A-Za-z /]+:|$)", body, re.DOTALL)
        hours_m = re.search(r"Hours Worked:\s*(.*?)(?=\n[A-Za-z /]+:|$)", body, re.DOTALL)
        links_m = re.search(r"Reference Links:\s*(.*?)(?=\n[A-Za-z /]+:|$)", body, re.DOTALL)
        learn_m = re.search(r"Learnings / Outcomes:\s*(.*?)(?=\n[A-Za-z /]+:|$)", body, re.DOTALL)
        block_m = re.search(r"Blockers / Risks:\s*(.*?)(?=\n[A-Za-z /]+:|$)", body, re.DOTALL)
        skills_m = re.search(r"Skills Used:\s*(.*?)(?=\n[A-Za-z /]+:|$)", body, re.DOTALL)
        
        entry = {
            "date_str": dt.strftime("%Y-%m-%d"),
            "display_date": dt.strftime("%d %B %Y"),
            "day_number": dt.day,
            "month_number": dt.month,
            "year": dt.year,
            "work_summary": summary_m.group(1).strip() if summary_m else "",
            "hours": hours_m.group(1).strip() if hours_m else "6.5",
            "links": links_m.group(1).strip() if links_m else "https://www.internship.edutainer.in/student/my-learning",
            "learnings": learn_m.group(1).strip() if learn_m else "",
            "blockers": block_m.group(1).strip() if block_m else "No major blockers encountered.",
            "skills": ["HTML", "CSS", "React.js"],
        }
        entries.append(entry)
        
    out_file = Path(__file__).parent / "pending_vtu_entries.json"
    out_file.write_text(json.dumps(entries, indent=2), encoding="utf-8")
    print(f"Extracted {len(entries)} diary entries to {out_file}")
    for e in entries:
        print(f"- {e['date_str']}: {e['work_summary'][:50]}...")

if __name__ == "__main__":
    parse_entries()
