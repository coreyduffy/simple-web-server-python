import io
import os
from typing import Any, BinaryIO

import pytest

# Only import main RequestHandler for integration tests
from simple_web_server.__main__ import RequestHandler


class MockSocket:
    """Mock socket class to simulate network communication."""

    def __init__(self) -> None:
        self.buffer = io.BytesIO()

    def sendall(self, data: bytes) -> None:
        self.buffer.write(data)

    def makefile(
        self, mode: str = "rb", buffering: int = -1, **kwargs: Any
    ) -> BinaryIO:
        """Mock makefile method to simulate socket file operations."""
        # Provide minimal valid HTTP request line + header for parsing during init
        return io.BytesIO(b"GET / HTTP/1.0\r\nHost: dummy\r\n\r\n")


class MockServer:
    """Mock server class to avoid port binding issues."""

    def __init__(self) -> None:
        self.server_address = ("localhost", 8080)


@pytest.fixture
def mock_socket() -> MockSocket:
    """Fixture to provide a mock socket for testing."""
    return MockSocket()


@pytest.fixture
def request_handler_instance(mock_socket: MockSocket) -> RequestHandler:
    """Fixture to provide a REAL RequestHandler instance for integration tests.
    Allows normal BaseHTTPRequestHandler init to parse the dummy request.
    """
    server = MockServer()
    # Initialize normally.
    handler = RequestHandler(mock_socket, ("127.0.0.1", 12345), server)
    return handler


# --- Integration Tests for RequestHandler.do_GET ---
# (These tests will automatically use temp_file and temp_dir from conftest.py)


def test_do_get_integration_file_exists(
    request_handler_instance: RequestHandler, mock_socket: MockSocket, temp_file: str
) -> None:
    """Integration test: do_GET correctly serves an existing file."""
    # Given
    file_name = os.path.basename(temp_file)
    request_handler_instance.path = f"/{file_name}"
    original_cwd = os.getcwd()
    os.chdir(os.path.dirname(temp_file))
    mock_socket.buffer = io.BytesIO()

    try:
        # When
        request_handler_instance.do_GET()

        # Then
        sent_data = mock_socket.buffer.getvalue()
        assert b"HTTP/1.0 200 OK" in sent_data
        assert b"Content-type: text/html" in sent_data
        assert b"Content-Length: 38" in sent_data
        assert b"<html><body>Test content</body></html>" in sent_data
    finally:
        os.chdir(original_cwd)


def test_do_get_integration_directory(
    request_handler_instance: RequestHandler, mock_socket: MockSocket, temp_dir: str
) -> None:
    """Integration test: do_GET correctly lists directory contents."""
    # Given
    dir_name = os.path.basename(temp_dir)
    request_handler_instance.path = f"/{dir_name}/"
    original_cwd = os.getcwd()
    os.chdir(os.path.dirname(temp_dir))
    mock_socket.buffer = io.BytesIO()

    try:
        # When
        request_handler_instance.do_GET()

        # Then
        sent_data = mock_socket.buffer.getvalue()
        assert b"HTTP/1.0 200 OK" in sent_data
        assert b"Content-type: text/html; charset=utf-8" in sent_data
        assert f"Directory listing for /{dir_name}/".encode() in sent_data
        assert b"file1.html" in sent_data
        assert b"file2.txt" in sent_data
        assert b"subdir/" in sent_data
    finally:
        os.chdir(original_cwd)


def test_do_get_integration_not_found(
    request_handler_instance: RequestHandler, mock_socket: MockSocket
) -> None:
    """Integration test: do_GET returns 404 for non-existent resource."""
    # Given
    request_handler_instance.path = "/nonexistent/thing.no"
    mock_socket.buffer = io.BytesIO()

    # When
    request_handler_instance.do_GET()

    # Then
    sent_data = mock_socket.buffer.getvalue()
    assert sent_data.startswith(
        b"HTTP/1.0 404 "
    ), f"Expected status line starting with 'HTTP/1.0 404 ', got: {sent_data[:50]}..."
    expected_header = b"Content-Type: text/html"
    assert expected_header in sent_data, (
        f"Expected '{expected_header.decode()}' header, "
        f"check response headers: {sent_data[:200]}..."
    )
    assert b"File/Directory not found: /nonexistent/thing.no" in sent_data


# --- Unit tests for handlers are now in tests/resource_handlers/ ---


if __name__ == "__main__":
    # If running this file directly, run pytest on the whole tests directory
    pytest.main(["tests"])
