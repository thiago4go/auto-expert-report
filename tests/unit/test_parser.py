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

# --- Sample Test Data ---

VALID_MARKDOWN_INPUT = """
# Chapter Title: Introduction to Asyncio

**Introduction:**
Asyncio is a library to write concurrent code using the async/await syntax.
It is perfect for IO-bound and high-level structured network code.
---

## Section 1: Core Concepts

Asyncio uses an event loop to manage tasks. `async def` defines a coroutine.
`await` pauses the coroutine until the awaited task completes.
---

## Section 2: Running Tasks

Use `asyncio.run()` to start the main entry point.
Use `asyncio.create_task()` to run coroutines concurrently.
---

**Summary:**
Asyncio provides powerful tools for building responsive and efficient asynchronous applications in Python.
---

**Keywords:**
- asyncio
- asynchronous
- concurrency
- event loop
- await
---

**Quiz:**

1.  **Question:** What keyword defines a coroutine function?
    *   `def async`
    *   `async def`
    *   `coroutine def`
    **Correct Answer:** `async def`

2.  **Question:** What function is typically used to start the asyncio event loop?
    *   `asyncio.start()`
    *   `asyncio.loop()`
    *   `asyncio.run()`
    **Correct Answer:** `asyncio.run()`

"""

VALID_MARKDOWN_NO_KEYWORDS = """
# Chapter Title: Basic Git Commands

**Introduction:**
Git is a distributed version control system.
---

## Section 1: Setup

`git config --global user.name "Your Name"`
`git config --global user.email "you@example.com"`
---

**Summary:**
Basic configuration is essential before starting.
---

**Quiz:**

1.  **Question:** What does Git track?
    *   Files
    *   Changes
    *   Users
    **Correct Answer:** Changes

"""

MISSING_TITLE_MARKDOWN = """
**Introduction:**
This input is missing the title line.
---
## Section 1: Problem
Content here.
---
**Summary:**
Summary here.
---
**Quiz:**
1. **Question:** Q?
   * A
   * B
   **Correct Answer:** A
"""

MISSING_SECTIONS_MARKDOWN = """
# Chapter Title: Missing Sections

**Introduction:**
This input has no sections defined between intro and summary.
---
**Summary:**
Summary here.
---
**Quiz:**
1. **Question:** Q?
   * A
   * B
   **Correct Answer:** A
"""

MISSING_QUIZ_MARKDOWN = """
# Chapter Title: Missing Quiz

**Introduction:**
Intro here.
---
## Section 1: Content
Some content.
---
**Summary:**
Summary here.
---
**Keywords:**
- missing
- quiz
"""

MALFORMED_QUIZ_ITEM_MARKDOWN = """
# Chapter Title: Malformed Quiz

**Introduction:**
Intro here.
---
## Section 1: Content
Some content.
---
**Summary:**
Summary here.
---
**Quiz:**

1.  **Question:** This question has no options or answer.

2.  **Question:** This question has options but no answer line?
    *   Option 1
    *   Option 2

3.  **Question:** This question has options and answer, but answer isn't an option?
    *   Red
    *   Blue
    **Correct Answer:** Green
"""

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


# --- Test parse_chapter_response Function ---

def test_parse_chapter_response_valid():
    """Test parsing a valid, complete Markdown input."""
    chapter = parse_chapter_response(VALID_MARKDOWN_INPUT)

    assert isinstance(chapter, Chapter)
    assert chapter.title == "Introduction to Asyncio"
    assert "Asyncio is a library" in chapter.introduction
    assert len(chapter.sections) == 2
    assert chapter.sections[0].heading == "Core Concepts"
    assert "event loop to manage tasks" in chapter.sections[0].content
    assert chapter.sections[1].heading == "Running Tasks"
    assert "Use `asyncio.run()`" in chapter.sections[1].content
    assert "responsive and efficient asynchronous applications" in chapter.summary
    assert chapter.keywords == [
        "asyncio",
        "asynchronous",
        "concurrency",
        "event loop",
        "await",
    ]
    assert len(chapter.quiz) == 2
    assert chapter.quiz[0].question == "What keyword defines a coroutine function?"
    assert chapter.quiz[0].options == ["`def async`", "`async def`", "`coroutine def`"]
    assert chapter.quiz[0].correct_answer == "`async def`"
    assert chapter.quiz[1].question == "What function is typically used to start the asyncio event loop?"
    assert chapter.quiz[1].options == ["`asyncio.start()`", "`asyncio.loop()`", "`asyncio.run()`"]
    assert chapter.quiz[1].correct_answer == "`asyncio.run()`"


def test_parse_chapter_response_valid_no_keywords():
    """Test parsing valid input without the optional keywords section."""
    chapter = parse_chapter_response(VALID_MARKDOWN_NO_KEYWORDS)

    assert isinstance(chapter, Chapter)
    assert chapter.title == "Basic Git Commands"
    assert "distributed version control system" in chapter.introduction
    assert len(chapter.sections) == 1
    assert chapter.sections[0].heading == "Setup"
    # Corrected assertion to check for the actual content parts
    assert '`git config --global user.name "Your Name"`' in chapter.sections[0].content
    assert '`git config --global user.email "you@example.com"`' in chapter.sections[0].content
    assert "Basic configuration is essential" in chapter.summary
    assert chapter.keywords is None # Should be None when section is missing
    assert len(chapter.quiz) == 1
    assert chapter.quiz[0].question == "What does Git track?"
    assert chapter.quiz[0].options == ["Files", "Changes", "Users"]
    assert chapter.quiz[0].correct_answer == "Changes"


def test_parse_chapter_response_missing_title():
    """Test ParseError when the title pattern is not found."""
    with pytest.raises(ParseError, match="Could not find chapter title"):
        parse_chapter_response(MISSING_TITLE_MARKDOWN)


def test_parse_chapter_response_missing_section():
    """Test ParseError when no sections are found."""
    with pytest.raises(ParseError, match="Could not find any sections"):
        parse_chapter_response(MISSING_SECTIONS_MARKDOWN)


def test_parse_chapter_response_missing_quiz():
    """Test ParseError when the quiz section is missing."""
    # Note: This assumes the Quiz section itself is mandatory, even if empty.
    # If an empty quiz section is valid, this test needs adjustment.
    with pytest.raises(ParseError, match="Could not find quiz section"):
        parse_chapter_response(MISSING_QUIZ_MARKDOWN)


def test_parse_chapter_response_malformed_quiz_item():
    """Test ParseError wrapping ValidationError for a malformed quiz item."""
    # The regex parses item 3, but it fails validation ("Green" not in ["Red", "Blue"]).
    # This results in a ParseError wrapping a ValidationError.
    with pytest.raises(ParseError, match="Parsed data failed validation"):
        try:
            parse_chapter_response(MALFORMED_QUIZ_ITEM_MARKDOWN)
        except ParseError as e:
            assert isinstance(e.__cause__, ValidationError)
            assert "Correct answer must be one of the provided options" in str(e)
            raise e


def test_parse_chapter_response_validation_error_quiz_explicit():
    """Test ParseError wrapping ValidationError for invalid quiz data."""
    # Test case 3 from MALFORMED_QUIZ_ITEM_MARKDOWN should parse but fail validation
    # because "Green" is not in ["Red", "Blue"].
    # We need to modify the input slightly to make it parse past the options check.
    invalid_validation_input = MALFORMED_QUIZ_ITEM_MARKDOWN.replace(
        "**Correct Answer:** Green", "**Correct Answer:** Green\n\n4. **Question:** Dummy"
    ) # Add dummy next question to ensure regex terminates correctly

    with pytest.raises(ParseError, match="Parsed data failed validation"):
        try:
            parse_chapter_response(invalid_validation_input)
        except ParseError as e:
            # Check that the cause was indeed a ValidationError
            assert isinstance(e.__cause__, ValidationError)
            assert "Correct answer must be one of the provided options" in str(e)
            raise e # Re-raise the caught ParseError to satisfy pytest.raises


def test_parse_chapter_response_empty_input():
    """Test ParseError with empty string input."""
    with pytest.raises(ParseError):
        parse_chapter_response("")


def test_parse_chapter_response_gibberish_input():
    """Test ParseError with input that doesn't match structure."""
    with pytest.raises(ParseError):
        parse_chapter_response("This is just random text.")
