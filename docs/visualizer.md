# Design Doc: Visualizer Module (`studyguide/visualizer.py`)

**Last Updated:** 2025-04-19

## 1. Purpose

The Visualizer module is responsible for generating a graphical representation (e.g., a flowchart or mind map) of the generated study guide's structure. This helps users quickly understand the relationship between chapters and sections.

## 2. Inputs

-   A list of `studyguide.parser.Chapter` objects, representing the complete study guide.
-   An output file path (string) where the generated diagram image should be saved.
-   Optional configuration parameters (e.g., diagram title, output format).

## 3. Outputs

-   A diagram image file (e.g., `.png`, `.svg`) saved to the specified output path.
-   The function will likely return `None` upon successful completion or raise an error.

## 4. Implementation Strategy

-   **Core Library:** Utilize the `diagrams` Python library (https://diagrams.mingrammer.com/).
-   **Structure:**
    -   Define a primary function, e.g., `create_study_guide_diagram(chapters: List[Chapter], output_filename: str, title: str = "Study Guide Structure")`.
    -   Inside this function:
        -   Instantiate a `Diagram` object from the `diagrams` library, providing the title and output filename (without the extension, as `diagrams` handles formats).
        -   Define diagram nodes using `diagrams` components (e.g., `Node`, `Cluster`).
        -   Iterate through the input `chapters` list.
        -   For each `Chapter`, create a `Cluster` representing the chapter.
        -   Within each chapter `Cluster`, create `Node` objects for the Introduction, each Section, Summary, and Quiz.
        -   Define edges (connections) between nodes to represent the flow or structure (e.g., Introduction -> Section 1 -> Section 2 -> ... -> Summary -> Quiz).
        -   Consider a top-level node representing the overall Study Guide topic, connected to each Chapter cluster.
-   **Error Handling:** Wrap diagram generation logic in `try...except` blocks to catch potential errors from the `diagrams` library or file system operations. Log errors using `structlog`.
-   **Dependencies:** Add `diagrams` to `requirements.txt`. Ensure Graphviz is installed on the system, as it's a runtime dependency for the `diagrams` library. (This might require a note in the README or setup instructions).

## 5. Alternatives Considered

-   **Graphviz directly:** More complex API compared to the `diagrams` abstraction.
-   **Mermaid:** While useful for text-based diagrams (like in Markdown), generating image files programmatically is less direct than using the `diagrams` library. `diagrams` is specifically designed for Python-based infrastructure/structure diagram generation.

## 6. Future Enhancements

-   Allow customization of node shapes, colors, and edge styles.
-   Support different diagram layouts (e.g., top-to-bottom, left-to-right).
-   Optionally embed keywords within the diagram nodes.
