import io
import os
import socket
import tempfile
from typing import Any, BinaryIO

import pytest

from simple_web_server.__main__ import RequestHandler


class MockRequest:
    """Mock request class to simulate HTTP requests."""

    def __init__(self, path: str = "/", command: str = "GET") -> None:
        self.path = path
        self.command = command


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
        return io.BytesIO(b"GET / HTTP/1.1\r\nHost: localhost\r\n\r\n")


class MockServer:
    """Mock server class to avoid port binding issues."""

    def __init__(self) -> None:
        self.server_address = ("localhost", 8080)


def find_free_port() -> int:
    """Find a free port to use for testing."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]


@pytest.fixture
def mock_socket() -> MockSocket:
    """Fixture to provide a mock socket for testing."""
    return MockSocket()


@pytest.fixture
def request_handler(mock_socket: MockSocket) -> RequestHandler:
    """Fixture to provide a RequestHandler instance with mocked socket."""
    server = MockServer()
    handler = RequestHandler(mock_socket, ("127.0.0.1", 12345), server)
    return handler


@pytest.fixture
def temp_file() -> str:
    """Fixture to create a temporary file for testing."""
    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write(b"<html><body>Test content</body></html>")
        return f.name


def test_send_page(request_handler: RequestHandler, mock_socket: MockSocket) -> None:
    """Test that send_page correctly sends HTTP headers and content."""
    # Given
    test_page: bytes = b"<html><body>Test</body></html>"

    # When
    request_handler.send_content(test_page)

    # Then
    sent_data = mock_socket.buffer.getvalue().decode("utf-8")
    assert "HTTP/1.0 200 OK" in sent_data
    assert "Content-type: text/html" in sent_data
    assert "Content-Length: 30" in sent_data
    assert test_page.decode("utf-8") in sent_data


def test_do_get_file_exists(
    request_handler: RequestHandler, mock_socket: MockSocket, temp_file: str
) -> None:
    """Test that do_GET correctly serves an existing file."""
    # Given
    request_handler.path = "/" + os.path.basename(temp_file)
    original_cwd = os.getcwd()
    os.chdir(os.path.dirname(temp_file))

    try:
        # When
        request_handler.do_GET()

        # Then
        sent_data = mock_socket.buffer.getvalue().decode("utf-8")
        assert "HTTP/1.0 200 OK" in sent_data
        assert "Content-type: text/html" in sent_data
        assert "Content-Length: 38" in sent_data
        assert "<html><body>Test content</body></html>" in sent_data
    finally:
        os.chdir(original_cwd)
        os.unlink(temp_file)


def test_do_get_file_not_found(
    request_handler: RequestHandler, mock_socket: MockSocket
) -> None:
    """Test that do_GET returns 404 for non-existent files."""
    # Given
    request_handler.path = "/nonexistent.html"

    # When
    request_handler.do_GET()

    # Then
    sent_data = mock_socket.buffer.getvalue().decode("utf-8")
    assert "HTTP/1.0 404 Error reading file:" in sent_data


def test_send_file(
    request_handler: RequestHandler, mock_socket: MockSocket, temp_file: str
) -> None:
    """Test that send_file correctly reads and sends file content."""
    # When
    request_handler.send_file(temp_file)

    # Then
    sent_data = mock_socket.buffer.getvalue().decode("utf-8")
    assert "HTTP/1.0 200 OK" in sent_data
    assert "Content-type: text/html" in sent_data
    assert "Content-Length: 38" in sent_data
    assert "<html><body>Test content</body></html>" in sent_data

    # Cleanup
    os.unlink(temp_file)


def test_send_file_error(
    request_handler: RequestHandler, mock_socket: MockSocket
) -> None:
    """Test that send_file raises an exception for file reading errors."""
    # Given
    nonexistent_file = "/nonexistent/file.html"

    # When-Then
    with pytest.raises(Exception) as exc_info:
        request_handler.send_file(nonexistent_file)
    assert "Error reading file:" in str(exc_info.value)


def test_send_content(request_handler: RequestHandler, mock_socket: MockSocket) -> None:
    """Test that send_content correctly sends HTTP headers and content."""
    # Given
    test_content = b"<html><body>Test</body></html>"

    # When
    request_handler.send_content(test_content)

    # Then
    sent_data = mock_socket.buffer.getvalue()
    assert b"HTTP/1.0 200 OK" in sent_data
    assert b"Content-type: text/html" in sent_data
    assert b"Content-Length: 30" in sent_data
    assert test_content in sent_data


if __name__ == "__main__":
    pytest.main()
