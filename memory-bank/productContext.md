# Product Context

*   **Related Brief:** projectbrief.md
*   **Last Updated:** 2025-04-19

## 1. Problem Statement

Users (students, researchers, etc.) often need concise, structured summaries or learning guides on specific topics. Manually compiling this information can be time-consuming and inefficient. Existing tools may lack the depth or structure required for effective learning.

## 2. Proposed Solution

This application automates the creation of a structured, five-chapter study guide on any given topic. It leverages the Perplexity AI API to generate relevant content, then parses, cleans, and formats this content into a user-friendly, responsive HTML document. It offers both a CLI for quick generation and an optional Streamlit UI for a visual preview.

## 3. User Experience Goals

*   **Simplicity:** Users should be able to generate a study guide with minimal effort, simply by providing a topic.
*   **Clarity:** The generated HTML guide should be easy to read, navigate, and understand, with clear chapter divisions.
*   **Responsiveness:** The HTML output must adapt well to various screen sizes (desktop, tablet, mobile).
*   **Efficiency:** The generation process should be reasonably fast, utilizing asynchronous API calls.

## 4. Key Features & Functionality

*   **Topic Input:** Accepts a string representing the desired study guide topic (via CLI or Streamlit UI).
*   **AI Content Generation:** Calls the Perplexity AI API to generate content for five distinct chapters based on the topic.
*   **Content Parsing & Structuring:** Parses the raw AI response, validates it (Pydantic), and potentially structures it further (pandas).
*   **HTML Rendering:** Uses Jinja2 templates and Tailwind CSS to create a styled, responsive, multi-page (or single-page with clear sections) HTML study guide.
*   **CLI Access:** Provides a command-line interface (Typer) for generating guides directly from the terminal.
*   **Web Preview (Optional):** Offers a Streamlit interface for topic input and previewing the generated guide.

## 5. Success Metrics

*   **Generation Success Rate:** Percentage of successful study guide generations without errors.
*   **User Satisfaction:** (Qualitative) Feedback on the quality and usefulness of the generated guides.
*   **API Usage Efficiency:** Monitoring Perplexity API token consumption and latency (via Prometheus metrics).
*   **Code Coverage:** Maintaining ≥90% test coverage.
*   **Performance:** Average time taken to generate a study guide.
