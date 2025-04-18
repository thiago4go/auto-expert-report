# Project Brief

*   **Project Name:** AI-Powered Study-Guide Generator
*   **Date Created:** 2025-04-19
*   **Version:** 0.1

## 1. Overview

This project is a Python application designed to automatically generate a five-chapter study guide based on a user-provided topic. It functions as both a Command Line Interface (CLI) tool and potentially a web application. The core process involves querying the Perplexity AI API asynchronously, parsing and structuring the received data, and finally rendering the study guide as responsive HTML pages. An optional Streamlit UI provides a preview capability.

## 2. Goals

*   Generate comprehensive, multi-chapter study guides automatically from a topic.
*   Leverage AI (Perplexity) for content generation.
*   Ensure efficient and robust interaction with the AI API using async patterns.
*   Produce well-structured, clean data from the AI responses.
*   Render user-friendly, responsive HTML output.
*   Provide both a CLI and an optional web preview interface.
*   Maintain high code quality through linting, formatting, and testing.

## 3. Scope

### In Scope

*   Accepting a topic string as input via CLI or UI.
*   Making asynchronous calls to the Perplexity AI API.
*   Parsing and validating AI responses using Pydantic.
*   Structuring parsed data, potentially using pandas.
*   Generating a five-chapter study guide in HTML format using Jinja2 templates.
*   Styling HTML output using Tailwind CSS (minified).
*   Providing a CLI interface using Typer.
*   Providing an optional preview UI using Streamlit.
*   Implementing structured logging using `structlog`.
*   Exposing Prometheus metrics for observability.
*   Unit and integration testing with pytest-asyncio (≥90% coverage).
*   Code linting (Ruff) and formatting (Black).

### Out of Scope

*   User accounts or authentication.
*   Saving/managing previously generated guides (beyond temporary output).
*   Support for AI models other than Perplexity.
*   Advanced UI features beyond basic topic input and preview.
*   Real-time collaboration features.

## 4. Target Audience

*   Students, researchers, or individuals needing structured summaries or learning materials on specific topics.
*   Developers looking for an example of integrating AI APIs into a Python application.

## 5. Key Stakeholders

*   Development Team
*   End Users (learners, researchers)
