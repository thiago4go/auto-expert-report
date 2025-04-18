"""
Unit tests for the studyguide.visualizer module.
"""

import os
import pytest
from unittest.mock import patch, MagicMock, call

# Assume Chapter, Section, QuizItem are importable for test data creation
# If they are in studyguide.parser, import them
try:
    from studyguide.parser import Chapter, Section, QuizItem
except ImportError:
    # Simple placeholders if parser isn't available or causes issues during isolated test runs
    class MockChapter:
        def __init__(self, title, introduction, sections, summary, quiz, keywords=None):
            self.title = title
            self.introduction = introduction
            self.sections = sections
            self.summary = summary
            self.quiz = quiz
            self.keywords = keywords

    class MockSection:
        def __init__(self, heading, content):
            self.heading = heading
            self.content = content

    class MockQuizItem:
         def __init__(self, question, options, correct_answer):
            self.question = question
            self.options = options
            self.correct_answer = correct_answer

    Chapter = MockChapter
    Section = MockSection
    QuizItem = MockQuizItem


# Import the function to test (it doesn't exist yet, but we write tests first)
# We expect it to be in studyguide/visualizer.py
try:
    from studyguide.visualizer import create_study_guide_diagram
except ImportError:
    # Define a dummy function if the actual one doesn't exist yet
    def create_study_guide_diagram(chapters, output_filename, title="Study Guide Structure"):
        print(f"Dummy create_study_guide_diagram called with {len(chapters)} chapters.")
        # Simulate file creation for tests that check existence
        if chapters: # Only create if there's data, prevents errors in empty list tests
             # Ensure the directory exists
            os.makedirs(os.path.dirname(output_filename), exist_ok=True)
            # Create a dummy file
            with open(f"{output_filename}.png", "w") as f:
                f.write("dummy diagram content")
        pass


# --- Test Data ---

@pytest.fixture
def sample_chapters():
    """Provides a list of Chapter objects for testing."""
    sec1 = Section(heading="S1: Basics", content="...")
    sec2 = Section(heading="S2: Advanced", content="...")
    quiz1 = QuizItem(question="Q1?", options=["A", "B"], correct_answer="A")
    ch1 = Chapter(
        title="Chapter 1: Foo",
        introduction="Intro Foo",
        sections=[sec1],
        summary="Summary Foo",
        quiz=[quiz1],
        keywords=["foo", "basic"],
    )
    ch2 = Chapter(
        title="Chapter 2: Bar",
        introduction="Intro Bar",
        sections=[sec2],
        summary="Summary Bar",
        quiz=[quiz1], # Re-use quiz for simplicity
        keywords=["bar", "advanced"],
    )
    return [ch1, ch2]


# --- Test Cases ---

@patch("studyguide.visualizer.Diagram") # Mock the Diagram class
@patch("studyguide.visualizer.Cluster") # Mock the Cluster class
@patch("studyguide.visualizer.Node")    # Mock the Node class
@patch("studyguide.visualizer.os.makedirs") # Mock makedirs
@patch("builtins.open") # Mock open to avoid file writing
def test_create_diagram_success(
    mock_open, mock_makedirs, mock_node, mock_cluster, mock_diagram, sample_chapters, tmp_path
):
    """Test successful diagram creation with mock objects."""
    mock_diagram_instance = MagicMock()
    mock_diagram.return_value.__enter__.return_value = mock_diagram_instance # Handle context manager

    output_base = tmp_path / "study_guide"
    output_filename = str(output_base)
    diagram_title = "My Awesome Study Guide"

    create_study_guide_diagram(sample_chapters, output_filename, title=diagram_title)

    # 1. Check Diagram initialization (including directory and outformat)
    mock_diagram.assert_called_once_with(
        diagram_title,
        show=False,
        filename=output_base.name,
        outformat="png", # Default format used in implementation
        directory=str(tmp_path) # Directory is passed from tmp_path
    )

    # 2. Check Cluster creation (one per chapter, matching implementation label)
    assert mock_cluster.call_count == len(sample_chapters)
    mock_cluster.assert_any_call("Chapter: Chapter 1: Foo")
    mock_cluster.assert_any_call("Chapter: Chapter 2: Bar")

    # 3. Check Node creation (matching implementation labels with counts)
    # Expected nodes: 2 * (1 Intro + 1 Section + 1 Summary + 1 Quiz) = 8 nodes
    assert mock_node.call_count == 8
    # Use assert_has_calls or check call_args_list if order matters and mocks allow
    # For simplicity, using assert_any_call for each expected node label
    calls = [
        call("Introduction\n(2 words)"), # Intro Foo
        call("Section: S1: Basics\n(1 words)"), # ...
        call("Summary\n(2 words)"), # Summary Foo
        call("Quiz (1 Qs)"), # Quiz (1)
        call("Introduction\n(2 words)"), # Intro Bar
        call("Section: S2: Advanced\n(1 words)"), # ...
        call("Summary\n(2 words)"), # Summary Bar
        call("Quiz (1 Qs)") # Quiz (1)
    ]
    mock_node.assert_has_calls(calls, any_order=True)

    # 4. Check Edges (difficult to assert precisely with mocks, focus on counts/calls)
    # Expect connections like Intro -> Sec1 -> Summary -> Quiz within each cluster
    # This requires mocking the >> operator or edge creation methods if used explicitly.
    # For now, we trust the calls to Node/Cluster imply structure.
    # Example (if using >>): assert mock_node().__rshift__.call_count > 0

    # 5. Check directory creation (using the string representation of the path)
    mock_makedirs.assert_called_once_with(str(tmp_path), exist_ok=True)

    # 6. Check that the diagram context manager was exited (implies saving)
    # __exit__ is called on the object returned by Diagram(), which is mock_diagram.return_value
    assert mock_diagram.return_value.__exit__.called


@patch("studyguide.visualizer.Diagram")
@patch("studyguide.visualizer.Cluster")
@patch("studyguide.visualizer.Node")
@patch("studyguide.visualizer.os.makedirs")
@patch("builtins.open")
@patch("studyguide.visualizer.logger") # Mock logger
def test_create_diagram_empty_list(
    mock_logger, mock_open, mock_makedirs, mock_node, mock_cluster, mock_diagram, tmp_path
):
    """Test diagram creation with an empty list of chapters."""
    output_base = tmp_path / "empty_guide"
    output_filename = str(output_base)
    diagram_title = "Empty Guide"

    create_study_guide_diagram([], output_filename, title=diagram_title)

    # Assert Diagram is called with correct args, including directory and format
    mock_diagram.assert_called_once_with(
        diagram_title,
        show=False,
        filename=output_base.name,
        outformat="png",
        directory=str(tmp_path)
    )
    # No clusters should be created
    mock_cluster.assert_not_called()
    # A single "Empty Guide" node should be created inside the diagram context
    mock_node.assert_called_once_with("Empty Guide")

    # Directory might still be created, assert with string path
    mock_makedirs.assert_called_once_with(str(tmp_path), exist_ok=True)

    # Check if a warning was logged
    mock_logger.warning.assert_called_once_with("No chapters provided, creating an empty diagram.")


@patch("studyguide.visualizer.Diagram", side_effect=FileNotFoundError("Graphviz not found"))
@patch("studyguide.visualizer.logger") # Mock logger
def test_create_diagram_graphviz_missing(mock_logger, mock_diagram, sample_chapters, tmp_path):
    """Test handling when Graphviz dependency is missing."""
    output_filename = str(tmp_path / "no_graphviz")

    with pytest.raises(FileNotFoundError): # Expect the original error to be raised or wrapped
         create_study_guide_diagram(sample_chapters, output_filename)

    # Check if an error was logged (matching the implementation's log call)
    mock_logger.error.assert_called_with(
        "Graphviz not found. Please install it to generate diagrams.",
        error="Graphviz not found", # Match the extra kwarg
        exc_info=True
    )


@patch("studyguide.visualizer.Diagram")
@patch("studyguide.visualizer.Cluster")
@patch("studyguide.visualizer.Node")
@patch("studyguide.visualizer.os.makedirs", side_effect=PermissionError("Cannot write"))
@patch("studyguide.visualizer.logger") # Mock logger
def test_create_diagram_permission_error(
    mock_logger, mock_makedirs, mock_node, mock_cluster, mock_diagram, sample_chapters, tmp_path
):
    """Test handling of file system permission errors."""
    output_filename = str(tmp_path / "protected_dir" / "permission_denied")

    with pytest.raises(PermissionError): # Expect the original error
        create_study_guide_diagram(sample_chapters, output_filename)

    # Check if an error was logged (matching the implementation's log call)
    mock_logger.error.assert_called_with(
        "Permission denied when trying to create diagram directory or file.", # Match exact text
        path=str(tmp_path / "protected_dir"),
        error="Cannot write", # Match the extra kwarg
        exc_info=True
    )
    # Diagram shouldn't be attempted if makedirs fails
    mock_diagram.assert_not_called()


# Test for adding the dependency - this is more of a reminder/check
def test_dependency_added():
    """Check if 'diagrams' is in requirements.txt."""
    try:
        with open("requirements.txt", "r") as f:
            content = f.read()
            assert "diagrams" in content
    except FileNotFoundError:
        pytest.fail("requirements.txt not found.")
