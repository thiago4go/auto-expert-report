"""
Unit tests for the studyguide.parser module.
"""

import pytest
from pydantic import ValidationError

from studyguide.parser import (
    Chapter,
    ParseError,
    QuizItem,
    Section,
    parse_chapter_response,
)


# --- Test Pydantic Models ---
def test_quiz_item_valid():
    """Test successful creation of a valid QuizItem."""
    item = QuizItem(
        question="What is Python?",
        options=["Language", "Snake", "Tool"],
        correct_answer="Language",
    )
    assert item.question == "What is Python?"
    assert item.options == ["Language", "Snake", "Tool"]
    assert item.correct_answer == "Language"


def test_quiz_item_invalid_correct_answer():
    """Test ValidationError when correct_answer is not in options."""
    with pytest.raises(ValidationError) as excinfo:
        QuizItem(
            question="What is FastAPI?",
            options=["Framework", "Library", "Language"],
            correct_answer="Tool",  # Not in options
        )
    assert "Correct answer must be one of the provided options" in str(
        excinfo.value
    )


def test_quiz_item_invalid_min_options():
    """Test ValidationError when less than 2 options are provided."""
    with pytest.raises(ValidationError) as excinfo:
        QuizItem(
            question="Is this valid?",
            options=["Yes"],  # Only one option
            correct_answer="Yes",
        )
    # Check for Pydantic's specific error message for list length (Pydantic v2)
    assert "List should have at least 2 items" in str(excinfo.value)


def test_section_valid():
    """Test successful creation of a valid Section."""
    section = Section(heading="Introduction", content="This is the intro.")
    assert section.heading == "Introduction"
    assert section.content == "This is the intro."


def test_chapter_valid():
    """Test successful creation of a valid Chapter."""
    quiz1 = QuizItem(
        question="Q1", options=["A", "B"], correct_answer="A"
    )
    quiz2 = QuizItem(
        question="Q2", options=["X", "Y", "Z"], correct_answer="Z"
    )
    sec1 = Section(heading="H1", content="C1")
    sec2 = Section(heading="H2", content="C2")

    chapter = Chapter(
        title="Test Chapter",
        introduction="Intro text.",
        sections=[sec1, sec2],
        summary="Summary text.",
        quiz=[quiz1, quiz2],
        keywords=["test", "chapter"],
    )
    assert chapter.title == "Test Chapter"
    assert chapter.introduction == "Intro text."
    assert len(chapter.sections) == 2
    assert chapter.sections[0].heading == "H1"
    assert chapter.summary == "Summary text."
    assert len(chapter.quiz) == 2
    assert chapter.quiz[1].question == "Q2"
    assert chapter.keywords == ["test", "chapter"]


def test_chapter_missing_optional_keywords():
    """Test Chapter creation when optional keywords are None."""
    quiz1 = QuizItem(
        question="Q1", options=["A", "B"], correct_answer="A"
    )
    sec1 = Section(heading="H1", content="C1")
    chapter = Chapter(
        title="Test Chapter",
        introduction="Intro text.",
        sections=[sec1],
        summary="Summary text.",
        quiz=[quiz1],
        # keywords is omitted, should default to None
    )
    assert chapter.keywords is None


def test_chapter_missing_required_field():
    """Test ValidationError when a required field (e.g., title) is missing."""
    with pytest.raises(ValidationError) as excinfo:
        Chapter(
            # title="Missing Title", # Intentionally missing
            introduction="Intro text.",
            sections=[Section(heading="H1", content="C1")],
            summary="Summary text.",
            quiz=[
                QuizItem(question="Q1", options=["A", "B"], correct_answer="A")
            ],
        )
    assert "title" in str(excinfo.value)
    # Check for Pydantic's specific error message for missing field (Pydantic v2)
    assert "Field required" in str(excinfo.value)


# --- Test parse_chapter_response Function (Placeholder) ---
def test_parse_chapter_response_placeholder():
    """
    Test the placeholder parse_chapter_response function.
    It currently ignores input and returns dummy data.
    """
    raw_input = """
    # Some Markdown Input

    This shouldn't affect the current placeholder output.
    """
    try:
        chapter = parse_chapter_response(raw_input)
        assert isinstance(chapter, Chapter)
        # Check if it returns the specific dummy data defined in the placeholder
        assert chapter.title == "Placeholder Title"
        assert len(chapter.sections) == 2
        assert chapter.sections[0].heading == "Section 1"
        assert len(chapter.quiz) == 2
        assert chapter.quiz[0].question == "Q1?"
        assert chapter.keywords == ["keyword1", "keyword2"]
    except ParseError as e:
        pytest.fail(f"Placeholder parse_chapter_response raised ParseError: {e}")
    except ValidationError as e:
        pytest.fail(
            f"Placeholder parse_chapter_response raised ValidationError: {e}"
        )


# Note: More tests will be needed here once the actual parsing logic
# in parse_chapter_response is implemented. These tests would cover:
# - Parsing various valid Markdown-like inputs.
# - Handling malformed inputs (raising ParseError).
# - Edge cases in formatting.
