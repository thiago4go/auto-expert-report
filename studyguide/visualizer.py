"""
Generates graphical diagrams representing the study guide structure.
"""

import os
from typing import List

import structlog
from diagrams import Cluster, Diagram, Node

# Assuming Chapter is defined in studyguide.parser
try:
    from studyguide.parser import Chapter
except ImportError:
    # Fallback for potential standalone use or testing issues
    logger = structlog.get_logger()
    logger.warning("Could not import Chapter from studyguide.parser. Using placeholder.")
    class Chapter: # type: ignore
        def __init__(self, title, introduction, sections, summary, quiz, keywords=None):
            self.title = title
            self.introduction = introduction
            self.sections = sections
            self.summary = summary
            self.quiz = quiz
            self.keywords = keywords

# Configure logger for this module
logger = structlog.get_logger()

# Define custom node attributes for better visual distinction if needed
# Example:
# graph_attr = {
#     "fontsize": "12",
#     "bgcolor": "transparent"
# }
# node_attr = {
#     "shape": "box",
#     "style": "rounded",
#     "fontsize": "10"
# }
# cluster_attr = {
#     "fontsize": "12",
#     "style": "rounded",
#     "bgcolor": "lightgrey"
# }

def create_study_guide_diagram(
    chapters: List[Chapter],
    output_filename: str,
    title: str = "Study Guide Structure",
    output_format: str = "png", # Default format
) -> None:
    """
    Generates a diagram of the study guide structure using the diagrams library.

    Args:
        chapters: A list of Chapter objects.
        output_filename: The base path and name for the output file (e.g., 'output/study_guide').
                         The format extension will be added automatically.
        title: The title of the diagram.
        output_format: The output format for the diagram (e.g., 'png', 'svg', 'jpg').

    Raises:
        FileNotFoundError: If Graphviz executable is not found.
        PermissionError: If there's an issue writing the file or creating directories.
        Exception: For other errors during diagram generation.
    """
    output_dir = os.path.dirname(output_filename)
    base_name = os.path.basename(output_filename)

    logger.info(
        "Starting diagram generation",
        output_file=f"{output_filename}.{output_format}",
        title=title,
        chapter_count=len(chapters),
    )

    if not chapters:
        logger.warning("No chapters provided, creating an empty diagram.")
        # Still attempt to create the directory and an empty diagram for consistency
        # Or decide to skip file creation entirely? Let's create it for now.

    try:
        # Ensure the output directory exists
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            logger.debug("Ensured output directory exists", path=output_dir)

        # Use diagrams context manager
        # Note: filename in Diagram is the base name without extension or path
        with Diagram(
            title,
            show=False,
            filename=base_name,
            outformat=output_format,
            # graph_attr=graph_attr, # Optional styling
            # node_attr=node_attr,   # Optional styling
            # cluster_attr=cluster_attr # Optional styling
            # The actual file will be saved in the CWD relative to 'filename',
            # so we might need to move it or handle paths carefully if CWD isn't output_dir.
            # Let's assume diagrams saves relative to CWD for now.
            # We will move the file later if needed, or adjust path handling.
            # For simplicity, let's assume output_filename includes the desired path.
            # Correction: `filename` is just the base, `directory` attr can specify path.
            directory=output_dir if output_dir else ".", # Specify output directory
        ) as diag:
            # Create a top-level node for the overall guide (optional)
            # guide_node = Node("Study Guide Topic") # Example

            if not chapters:
                 Node("Empty Guide") # Add a node for empty diagrams

            for chapter in chapters:
                chapter_label = f"Chapter: {chapter.title}"
                with Cluster(chapter_label):
                    # Create nodes within the chapter cluster
                    intro_node = Node(f"Introduction\n({len(chapter.introduction.split())} words)")
                    section_nodes = [
                        Node(f"Section: {sec.heading}\n({len(sec.content.split())} words)")
                        for sec in chapter.sections
                    ]
                    summary_node = Node(f"Summary\n({len(chapter.summary.split())} words)")
                    quiz_node = Node(f"Quiz ({len(chapter.quiz)} Qs)")

                    # Define edges for flow within the chapter
                    current_node = intro_node
                    if section_nodes:
                        current_node >> section_nodes[0] # Intro -> First Section
                        for i in range(len(section_nodes) - 1):
                            section_nodes[i] >> section_nodes[i+1] # Section -> Next Section
                        current_node = section_nodes[-1] # Last section becomes current

                    current_node >> summary_node # Last Section (or Intro) -> Summary
                    summary_node >> quiz_node    # Summary -> Quiz

                    # Connect top-level guide node to this chapter cluster (optional)
                    # guide_node >> intro_node # Or connect to the cluster itself if preferred

        logger.info(
            "Diagram generated successfully",
            output_file=f"{output_filename}.{output_format}",
        )

    except FileNotFoundError as e:
        # Specific check for Graphviz missing (common issue with diagrams)
        if "dot" in str(e).lower() or "graphviz" in str(e).lower():
             logger.error(
                 "Graphviz not found. Please install it to generate diagrams.",
                 error=str(e),
                 exc_info=True,
             )
             # Re-raise the specific error for clarity
             raise FileNotFoundError("Graphviz executable not found. Please install it.") from e
        else:
             # Other file not found errors (e.g., bad output path?)
             logger.error("File not found error during diagram generation", error=str(e), exc_info=True)
             raise
    except PermissionError as e:
        logger.error(
            "Permission denied when trying to create diagram directory or file.",
            path=output_dir or ".",
            error=str(e),
            exc_info=True,
        )
        raise
    except Exception as e:
        logger.exception(
            "An unexpected error occurred during diagram generation",
            error=str(e),
        )
        raise
