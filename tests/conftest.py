import io
import os
import tempfile
from collections.abc import Generator
from unittest.mock import MagicMock

import pytest

# Import RequestHandler for type hinting the mock
from simple_web_server.__main__ import RequestHandler


@pytest.fixture
def mock_request_handler() -> MagicMock:
    """Fixture to provide a MOCKED RequestHandler for handler unit tests."""
    # Create a mock object that mimics the RequestHandler interface
    mock = MagicMock(spec=RequestHandler)
    mock.path = "/mock/path"  # Set a default path for the mock
    # Mock the wfile attribute with a BytesIO object to capture writes
    mock.wfile = io.BytesIO()
    # Ensure necessary methods used by handlers are present on the mock
    mock.send_response = MagicMock()
    mock.send_header = MagicMock()
    mock.end_headers = MagicMock()
    mock.send_error = MagicMock()
    return mock


@pytest.fixture
def temp_file() -> Generator[str, None, None]:
    """Fixture to create a temporary file with content for testing."""
    # Create a temporary file, ensuring it has a common web extension
    with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as f:
        f.write(b"<html><body>Test content</body></html>")
        filepath = f.name
    # Yield the path so the test can use it
    yield filepath
    # Cleanup: remove the file after the test finishes
    os.unlink(filepath)


@pytest.fixture
def temp_dir() -> Generator[str, None, None]:
    """Fixture to create a temporary directory with files/subdirs for testing."""
    # Create a temporary directory
    temp_dir_path = tempfile.mkdtemp()
    # Create some test files and a subdirectory inside it
    with open(os.path.join(temp_dir_path, "file1.html"), "w") as f:
        f.write("<html><body>File 1</body></html>")
    with open(os.path.join(temp_dir_path, "file2.txt"), "w") as f:
        f.write("Text file content")
    os.mkdir(os.path.join(temp_dir_path, "subdir"))
    # Yield the directory path for the test
    yield temp_dir_path
    # Cleanup: recursively remove the directory and its contents
    for root, dirs, files in os.walk(temp_dir_path, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))
    os.rmdir(temp_dir_path)
