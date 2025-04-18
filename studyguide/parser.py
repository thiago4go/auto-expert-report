"""
Parses raw text content (expected from Perplexity API) into structured Pydantic models.
"""

import re
from typing import Any, Dict, List, Optional

import structlog
from pydantic import (
    BaseModel,
    Field,
    ValidationError,
    field_validator,
    model_validator,
)

logger = structlog.get_logger(__name__)


class ParseError(Exception):
    """Custom exception for parsing failures."""

    pass


class QuizItem(BaseModel):
    """Represents a single quiz question with options and the correct answer."""

    question: str = Field(..., description="The quiz question.")
    options: List[str] = Field(
        ..., min_length=2, description="List of possible answers."
    )
    correct_answer: str = Field(
        ..., description="The correct answer from the options."
    )

    @field_validator("correct_answer")
    def correct_answer_must_be_in_options(
        cls, v: str, values: Dict[str, Any]
    ) -> str:
        """Validate that the correct answer is indeed one of the options."""
        # Note: Pydantic v2 validators run *after* individual field validation.
        # 'values' here is actually the model's data dictionary.
        options = values.data.get("options")
        if options and v not in options:
            logger.error(
                "Validation Error: Correct answer not in options",
                correct_answer=v,
                options=options,  # Use the variable 'options' defined above
            )
            raise ValueError(
                "Correct answer must be one of the provided options"
            )
        return v


class Section(BaseModel):
    """Represents a section within a chapter, containing a heading and content."""

    heading: str = Field(..., description="The heading of the section.")
    content: str = Field(..., description="The main content of the section.")


class Chapter(BaseModel):
    """Represents a complete study guide chapter."""

    title: str = Field(..., description="The title of the chapter.")
    introduction: str = Field(
        ..., description="An introductory paragraph for the chapter."
    )
    sections: List[Section] = Field(
        ..., description="A list of sections within the chapter."
    )
    summary: str = Field(
        ..., description="A concluding summary for the chapter."
    )
    quiz: List[QuizItem] = Field(
        ..., description="A list of quiz questions for the chapter."
    )
    keywords: Optional[List[str]] = Field(
        None, description="Optional list of keywords for the chapter."
    )


def parse_chapter_response(raw_text: str) -> Chapter:
    """
    Parses raw text (expected Markdown-like format) into a Chapter object.

    Args:
        raw_text: The raw string response from the AI API.

    Returns:
        A populated Chapter object.

    Raises:
        ParseError: If the text cannot be parsed into the Chapter structure.
        ValidationError: If the extracted data fails Pydantic validation.
    """
    logger.info("Starting chapter response parsing")
    # --- Parsing Logic Placeholder ---
    # This section needs implementation based on the actual API output format.
    # It will involve regex or string splitting to extract:
    # - Title
    # - Introduction
    # - Sections (Headings + Content)
    # - Summary
    # - Quiz (Questions, Options, Correct Answers)
    # - Keywords (Optional)
    #
    # Example (Conceptual - Needs Refinement):
    try:
        # Dummy data for structure demonstration - REPLACE WITH ACTUAL PARSING
        title = "Placeholder Title"
        introduction = "Placeholder Introduction."
        sections = [
            Section(heading="Section 1", content="Content 1."),
            Section(heading="Section 2", content="Content 2."),
        ]
        summary = "Placeholder Summary."
        quiz = [
            QuizItem(
                question="Q1?",
                options=["A", "B", "C"],
                correct_answer="A",
            ),
            QuizItem(
                question="Q2?",
                options=["X", "Y"],
                correct_answer="Y",
            ),
        ]
        keywords = ["keyword1", "keyword2"]

        chapter_data = {
            "title": title,
            "introduction": introduction,
            "sections": sections,
            "summary": summary,
            "quiz": quiz,
            "keywords": keywords,
        }

        chapter = Chapter(**chapter_data)
        logger.info("Successfully parsed chapter response", title=chapter.title)
        return chapter

    except ValidationError as e:
        logger.error("Pydantic validation failed during parsing", error=e)
        raise  # Re-raise the validation error
    except Exception as e:
        logger.error(
            "Failed to parse chapter response due to unexpected error",
            exc_info=True,
        )
        raise ParseError(f"Could not parse raw text: {e}") from e
