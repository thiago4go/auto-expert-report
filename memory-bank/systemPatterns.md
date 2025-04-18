# System Patterns

*   **Related Brief:** projectbrief.md
*   **Last Updated:** 2025-04-19

## 1. Architecture Overview

The system follows a modular pipeline architecture. Input (topic) is received via the CLI (Typer) or Web UI (Streamlit). An `Engine` component orchestrates the process: it uses an `APIClient` to asynchronously fetch data from the Perplexity API, a `Parser` (using Pydantic, potentially pandas) to structure the response, and a `Renderer` (Jinja2) to generate the final HTML output. Configuration is managed centrally, and logging (`structlog`) provides observability.

```mermaid
graph LR
    subgraph User Interface
        direction LR
        CLI[CLI (Typer)]
        UI[Web UI (Streamlit)]
    end

    subgraph Core Logic
        direction TB
        Engine[Engine (Orchestrator)]
        APIClient[API Client (httpx, asyncio, tenacity)]
        Parser[Parser (Pydantic, pandas)]
        Renderer[Renderer (Jinja2, Tailwind)]
        Config[Configuration]
        Logger[Logging (structlog)]
    end

    subgraph External Services
        Perplexity[Perplexity AI API]
    end

    subgraph Output
        HTML[HTML Study Guide]
    end

    CLI --> Engine
    UI --> Engine
    Engine --> Config
    Engine --> Logger
    Engine --> APIClient
    Engine --> Parser
    Engine --> Renderer
    APIClient --> Perplexity
    Perplexity --> APIClient
    APIClient --> Parser
    Parser --> Renderer
    Renderer --> HTML

    %% Styling for readability
    classDef core fill:#f9f,stroke:#333,stroke-width:2px;
    classDef ui fill:#ccf,stroke:#333,stroke-width:2px;
    classDef external fill:#cfc,stroke:#333,stroke-width:2px;
    classDef output fill:#ffc,stroke:#333,stroke-width:2px;

    class CLI,UI ui;
    class Engine,APIClient,Parser,Renderer,Config,Logger core;
    class Perplexity external;
    class HTML output;
```

## 2. Key Technical Decisions

*   **Asynchronous API Calls (`httpx`, `asyncio`):** Chosen for I/O-bound efficiency when interacting with the external Perplexity API, preventing blocking and improving responsiveness.
*   **Single Shared `httpx.AsyncClient`:** To leverage connection pooling and improve performance for multiple API calls within a single generation process.
*   **Retry Logic (`tenacity`):** Implemented for resilience against transient network issues or API errors, using exponential back-off.
*   **Pydantic for Parsing/Validation:** Ensures data integrity and structure from the potentially variable AI API responses. Provides clear data models.
*   **Jinja2 for Templating:** Standard Python templating engine, flexible for generating structured HTML.
*   **Tailwind CSS:** Utility-first CSS framework for rapid development of responsive UI styles, compiled to minimize final CSS size.
*   **Typer for CLI:** Modern and easy-to-use library for creating robust command-line interfaces with type hints.
*   **Streamlit for Optional UI:** Simple way to provide a web-based preview without building a full-stack web application.
*   **Structured Logging (`structlog`):** Produces machine-readable (JSON) logs, facilitating easier analysis and integration with log management systems.
*   **Composition over Inheritance:** Preferred design principle to maintain flexibility and avoid deep class hierarchies.
*   **Pre-commit Hooks (Black, Ruff):** Enforces code quality and consistency automatically before commits.

## 3. Design Patterns

*   **Pipeline:** The overall study guide generation follows a sequential processing pipeline (Input -> Fetch -> Parse -> Render -> Output).
*   **Dependency Injection (Implicit/Explicit):** Components like the `APIClient`, `Parser`, `Renderer` are likely instantiated and passed into the `Engine` or accessed via a shared context, promoting decoupling and testability.
*   **Configuration Management:** Centralized configuration likely loaded at startup (e.g., from environment variables or a config file) and accessed by various components.
*   **Retry Pattern:** Implemented using `tenacity` for robust API interactions.

## 4. Component Relationships

*   **`cli.py` / `preview.py`:** Entry points, capture user input (topic) and initiate the generation process by calling the `Engine`.
*   **`engine.py`:** Orchestrates the workflow. Calls `api_client.py` to fetch data, `parser.py` to process it, and `renderer.py` to generate HTML. Uses `config.py` for settings and `logging_config.py` for logging setup.
*   **`api_client.py`:** Handles all communication with the Perplexity API, including authentication (via environment variables), asynchronous requests (`httpx`), and retries (`tenacity`). Uses a shared `httpx.AsyncClient`.
*   **`parser.py`:** Takes raw API responses, validates them using Pydantic models, cleans the data, and structures it (potentially using pandas) into a format suitable for rendering.
*   **`renderer.py`:** Uses Jinja2 templates (`templates/`) and the parsed data to generate the final HTML output files (`site/` or `output/`). Interacts with Tailwind CSS build process indirectly.
*   **`config.py`:** Defines configuration settings (e.g., API endpoints, default parameters) often loaded from environment variables.
*   **`logging_config.py`:** Configures `structlog` for structured JSON logging throughout the application.

## 5. Critical Implementation Paths

*   **Study Guide Generation Flow:**
    1.  User provides topic via CLI or Streamlit UI.
    2.  `Engine` receives the topic.
    3.  `Engine` requests content generation from `APIClient`.
    4.  `APIClient` makes asynchronous calls (potentially multiple for 5 chapters) to Perplexity API, handling retries.
    5.  `APIClient` receives responses.
    6.  `Engine` passes responses to `Parser`.
    7.  `Parser` validates and structures the data using Pydantic models.
    8.  `Engine` passes structured data to `Renderer`.
    9.  `Renderer` uses Jinja2 templates and data to generate HTML files.
    10. HTML files are saved to the output directory (`site/` or `output/`).
    11. Result (path to output or preview) is presented to the user.
*   **Error Handling Flow:**
    1.  API call fails permanently (after retries) -> Log error, inform user via `Engine`.
    2.  Parsing fails (invalid response structure) -> Log error (Pydantic validation error), inform user via `Engine`.
    3.  Rendering fails (template error) -> Log error, inform user via `Engine`.
