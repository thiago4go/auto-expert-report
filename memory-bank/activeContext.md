# Active Context

*   **Related Brief:** projectbrief.md
*   **Related Product Context:** productContext.md
*   **Related System Patterns:** systemPatterns.md
*   **Related Tech Context:** techContext.md
*   **Last Updated:** 2025-04-19

## 1. Current Focus

Starting Phase 2 (Core Logic Implementation) following Test-Driven Development (TDD). The immediate task is to implement the unit tests for the recently created API Client module (`studyguide/api_client.py`).

## 2. Recent Changes

*   **Phase 1 Completion:** Successfully scaffolded the project structure, created configuration files (`.gitignore`, `requirements.txt`, `package.json`, `ruff.toml`, `pyproject.toml`, `.pre-commit-config.yaml`), implemented and tested the configuration (`studyguide/config.py`) and logging (`studyguide/logging_config.py`) modules, and set up Tailwind CSS (`tailwind.config.js`, `assets/input.css`, `assets/tailwind.css`). (Date: 2025-04-19)
*   **API Client Implementation:** Implemented the initial version of the asynchronous Perplexity API client (`studyguide/api_client.py`) including `httpx`, `tenacity` retries, `aiocache` (in-memory), and `structlog` integration. (Date: 2025-04-19)

## 3. Next Steps

*   Step 1: Implement unit tests for the API Client module in `tests/unit/test_api_client.py`.
*   Step 2: Proceed with implementing the Parser module (`studyguide/parser.py`) following TDD.

## 4. Active Decisions & Considerations

*   **TDD Adherence:** Continuing to follow Test-Driven Development for all core logic modules as planned.
*   **API Mocking Strategy:** Need to decide on the specific approach for mocking `httpx.AsyncClient` and `aiocache` in the upcoming API client tests (e.g., using `pytest-httpx`, custom mocks, `respx`).

## 5. Important Patterns & Preferences

*   **`.clinerules` Adherence:** Consistently applying project conventions defined in `.clinerules` (PEP 484 type hints, Ruff/Black formatting, async best practices, structured logging).
*   **Modular Design:** Maintaining the 7-module architecture agreed upon during planning.
*   **Configuration Management:** Using Pydantic with environment variables for configuration.

## 6. Learnings & Insights

*   **Tooling Setup:** The initial setup of linters (Ruff), formatters (Black), pre-commit hooks, and build tools (npm for Tailwind) was successful and integrates well with the project structure.
*   **Dependency Management:** Confirmed Node.js dependencies (`@tailwindcss/typography`) need explicit inclusion in `package.json` for `npm install` to work correctly with the config file.
