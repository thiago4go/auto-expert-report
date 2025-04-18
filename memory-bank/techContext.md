# Tech Context

*   **Related Brief:** projectbrief.md
*   **Last Updated:** 2025-04-19

## 1. Core Technologies

[List the primary languages, frameworks, and databases used.]

*   **Language(s):** [e.g., Python 3.11, TypeScript]
*   **Framework(s):** [e.g., FastAPI, React]
*   **Database(s):** [e.g., PostgreSQL, Redis]
*   **Runtime(s):** [e.g., Node.js v18]

## 2. Development Environment Setup

[Provide instructions or links to documentation on how to set up the development environment.]

*   **Prerequisites:** [e.g., Docker, Python 3.11]
*   **Setup Steps:**
    1.  Clone repository: `git clone ...`
    2.  Install dependencies: `pip install -r requirements.txt`
    3.  Configure environment variables (see `.env.example`).
    4.  Run database migrations: `alembic upgrade head`
    5.  Start application: `uvicorn main:app --reload`

## 3. Technical Constraints

[List any known technical limitations or constraints.]

*   Constraint 1: [e.g., Must run on Linux]
*   Constraint 2: [e.g., Limited third-party API rate limits]

## 4. Key Dependencies

[Highlight critical external libraries or services the project relies on.]

*   Dependency 1: [e.g., `httpx` for async HTTP requests]
*   Dependency 2: [e.g., Stripe API for payments]

## 5. Tool Usage Patterns

[Describe how specific tools are used in the development workflow.]

*   **Linting:** [e.g., Ruff, configured via `pyproject.toml`]
*   **Formatting:** [e.g., Black, run automatically via pre-commit hook]
*   **Testing:** [e.g., Pytest, run via `pytest tests/`]
*   **CI/CD:** [e.g., GitHub Actions, see `.github/workflows/`]
