# Tech Context

*   **Related Brief:** projectbrief.md
*   **Last Updated:** 2025-04-19

## 1. Core Technologies

*   **Language(s):** Python (PEP 484 type hints enforced)
*   **Framework(s):** Typer (CLI), Streamlit (Optional UI), Jinja2 (Templating)
*   **Libraries:** httpx (Async HTTP), asyncio (Concurrency), Pydantic (Parsing/Validation), pandas (Data Structure), tenacity (Retries), structlog (Logging), Tailwind CSS (Styling via `assets/tailwind.css` compiled from `assets/input.css`), Ruff (Linting), Black (Formatting), pytest-asyncio (Testing)
*   **AI Service:** Perplexity AI API

## 2. Development Environment Setup

*   **Prerequisites:** Python (version specified in `pyproject.toml` or `requirements.txt`), Node.js/npm (for Tailwind CSS compilation), Pre-commit (`pip install pre-commit && pre-commit install`)
*   **Setup Steps:**
    1.  Clone repository: `git clone ...`
    2.  Install Python dependencies: `pip install -r requirements.txt` (or using Poetry/PDM if `pyproject.toml` is configured for it)
    3.  Install Node.js dependencies: `npm install` (for Tailwind)
    4.  Compile Tailwind CSS: `npm run build:css` (or similar, check `package.json`)
    5.  Configure environment variables for Perplexity API Key (e.g., in a `.env` file - **ensure `.env` is in `.gitignore`**). Secrets are injected via environment variables.
    6.  Run application (CLI): `python -m studyguide.cli --topic "Your Topic"` (adjust command based on actual entry point)
    7.  Run application (Streamlit UI): `streamlit run app/preview.py` (adjust command based on actual entry point)

## 3. Technical Constraints

*   Requires internet connectivity for Perplexity API calls.
*   Dependent on Perplexity API availability and rate limits.
*   CPU-bound work (potentially parsing/structuring) should be offloaded using `asyncio.to_thread` to avoid blocking the event loop.
*   Secrets (like API keys) must be handled via environment variables, not hardcoded.

## 4. Key Dependencies

*   **`httpx`:** For making asynchronous HTTP requests to the Perplexity API. A single shared `AsyncClient` instance should be used.
*   **`asyncio`:** Core library for managing asynchronous operations.
*   **`pydantic`:** For parsing and validating the structure of responses from the Perplexity API.
*   **`jinja2`:** For rendering the final HTML study guide from templates.
*   **`typer`:** For building the command-line interface.
*   **`streamlit`:** For the optional web preview UI.
*   **`tenacity`:** Used to wrap outbound API calls with retry logic (exponential back-off).
*   **`structlog`:** For structured JSON logging.
*   **`ruff`:** For linting (warnings treated as errors).
*   **`black`:** For code formatting (line length 88).
*   **`pytest-asyncio`:** For testing asynchronous code.

## 5. Tool Usage Patterns

*   **Linting:** Ruff, configured via `ruff.toml`. Enforced via pre-commit hook.
*   **Formatting:** Black (line length 88), configured via `pyproject.toml`. Enforced via pre-commit hook.
*   **Testing:** Pytest with `pytest-asyncio`. Run via `pytest tests/`. Target ≥90% coverage. Unit tests in `tests/unit`, integration tests in `tests/integration`. HTML output snapshots stored in `tests/fixtures/`.
*   **Type Checking:** Adherence to PEP 484 type hints (likely checked by Ruff or a separate tool like MyPy).
*   **CSS:** Tailwind CSS compiled via npm script (e.g., `npm run build:css`).
*   **Dependency Management:** `requirements.txt` and `pyproject.toml`.
*   **Pre-commit Hooks:** Configured in `.pre-commit-config.yaml` to run Black and Ruff.
