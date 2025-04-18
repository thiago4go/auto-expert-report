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

logger = structlog.get_logger() # Use default logger name


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

from pydantic import (
    BaseModel,
    Field,
    ValidationError,
    ValidationInfo, # Import ValidationInfo
    field_validator,
    model_validator,
)

logger = structlog.get_logger() # Use default logger name


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
    def correct_answer_must_be_in_options(cls, v: str, info: ValidationInfo) -> str: # Change 'values' to 'info: ValidationInfo'
        """Validate that the correct answer is indeed one of the options."""
        # Pydantic v2: Access field values via the info.data dictionary
        # The validator receives the value `v` and the `info` object which has `info.data`
        options = info.data.get("options")
        if options and v not in options:
            logger.warning( # Use warning level for validation logic issues
                "Validation Warning: Correct answer not in options",
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
    logger.debug("Starting chapter response parsing", raw_text_length=len(raw_text))

    # Define regex patterns for extraction based on the assumed Markdown structure
    # Making patterns robust to variations in whitespace and line endings
    title_pattern = re.compile(r"^\s*#\s*Chapter Title:\s*(.+?)\s*$", re.MULTILINE)
    intro_pattern = re.compile(
        r"\*\*Introduction:\*\*\s*(.*?)\s*---", re.MULTILINE | re.DOTALL
    )
    section_pattern = re.compile(
        r"##\s*Section\s*\d+:\s*(.+?)\s*\n(.*?)\s*(?=(?:---|\Z))",
        re.MULTILINE | re.DOTALL,
    )
    summary_pattern = re.compile(
        r"\*\*Summary:\*\*\s*(.*?)\s*---", re.MULTILINE | re.DOTALL
    )
    keywords_pattern = re.compile(
        r"\*\*Keywords:\*\*\s*\n(.*?)(?=\n---|\Z)", re.MULTILINE | re.DOTALL
    )
    quiz_pattern = re.compile(
        r"\*\*Quiz:\*\*\s*(.*)", re.MULTILINE | re.DOTALL
    )
    quiz_item_pattern = re.compile(
        r"\d+\.\s*\*\*Question:\*\*\s*(.+?)\s*\n(.*?)\s*\*\*Correct Answer:\*\*\s*(.+?)\s*(?=\n\d+\.|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    quiz_option_pattern = re.compile(r"^\s*\*\s*(.+?)\s*$", re.MULTILINE)

    try:
        # Extract Title
        title_match = title_pattern.search(raw_text)
        if not title_match:
            raise ParseError("Could not find chapter title matching pattern.")
        title = title_match.group(1).strip()
        logger.debug("Extracted title", title=title)

        # Extract Introduction
        intro_match = intro_pattern.search(raw_text)
        if not intro_match:
            raise ParseError("Could not find introduction section.")
        introduction = intro_match.group(1).strip()
        logger.debug("Extracted introduction", length=len(introduction))

        # Extract Sections
        sections_data = section_pattern.findall(raw_text)
        if not sections_data:
            raise ParseError("Could not find any sections.")
        sections = [
            Section(heading=heading.strip(), content=content.strip())
            for heading, content in sections_data
        ]
        logger.debug("Extracted sections", count=len(sections))

        # Extract Summary
        summary_match = summary_pattern.search(raw_text)
        if not summary_match:
            raise ParseError("Could not find summary section.")
        summary = summary_match.group(1).strip()
        logger.debug("Extracted summary", length=len(summary))

        # Extract Keywords (Optional)
        keywords_match = keywords_pattern.search(raw_text)
        keywords = None
        if keywords_match:
            keyword_block = keywords_match.group(1).strip()
            # Extract keywords assuming they are bullet points
            keywords = [
                line.strip("-* ").strip()
                for line in keyword_block.split("\n")
                if line.strip()
            ]
            logger.debug("Extracted keywords", keywords=keywords)
        else:
            logger.debug("No keywords section found.")


        # Extract Quiz
        quiz_match = quiz_pattern.search(raw_text)
        if not quiz_match:
            raise ParseError("Could not find quiz section.")
        quiz_block = quiz_match.group(1).strip()

        quiz_items_data = quiz_item_pattern.findall(quiz_block)
        if not quiz_items_data:
            raise ParseError("Could not find any quiz items within the quiz section.")

        quiz = []
        for question, options_block, correct_answer in quiz_items_data:
            options = quiz_option_pattern.findall(options_block)
            if not options:
                 raise ParseError(f"Could not find options for question: {question[:50]}...")
            cleaned_options = [opt.strip() for opt in options]
            cleaned_correct_answer = correct_answer.strip()

            quiz_item = QuizItem(
                question=question.strip(),
                options=cleaned_options,
                correct_answer=cleaned_correct_answer,
            )
            quiz.append(quiz_item)
        logger.debug("Extracted quiz items", count=len(quiz))


        # Assemble Chapter object
        chapter_data = {
            "title": title,
            "introduction": introduction,
            "sections": sections,
            "summary": summary,
            "quiz": quiz,
            "keywords": keywords,
        }

        chapter = Chapter(**chapter_data)
        logger.info("Successfully parsed and validated chapter response", title=chapter.title)
        return chapter

    except ValidationError as e:
        logger.error(
            "Pydantic validation failed after parsing",
            error=str(e), # Log string representation for clarity
            details=e.errors(), # Log detailed errors
            title=title if 'title' in locals() else "Unknown",
        )
        # Wrap Pydantic error in ParseError for consistent exception type from this function
        raise ParseError(f"Parsed data failed validation: {e}") from e
    except Exception as e:
        # Catch regex errors or other unexpected issues during parsing
        logger.error(
            "Failed to parse chapter response due to unexpected error",
            error=str(e),
            exc_info=True, # Include traceback
        )
        # Ensure consistent error type is raised
        if not isinstance(e, ParseError):
             raise ParseError(f"Could not parse raw text: {e}") from e
        else:
             raise # Re-raise if it's already a ParseError
