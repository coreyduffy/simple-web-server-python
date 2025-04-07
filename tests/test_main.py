import io
from http.server import HTTPServer
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


@pytest.fixture
def mock_socket() -> MockSocket:
    """Fixture to provide a mock socket for testing."""
    return MockSocket()


@pytest.fixture
def request_handler(mock_socket: MockSocket) -> RequestHandler:
    """Fixture to provide a RequestHandler instance with mocked socket."""
    server = HTTPServer(("localhost", 8080), RequestHandler)
    handler = RequestHandler(mock_socket, ("127.0.0.1", 12345), server)
    return handler


def test_create_page(request_handler: RequestHandler) -> None:
    """Test that the create_page method generates correct HTML with request details."""
    # Given
    page = request_handler.create_page()

    # Then
    assert "<html>" in page
    assert "<body>" in page
    assert "<table>" in page
    assert "Date and time" in page
    assert "Client host" in page
    assert "Client port" in page
    assert "Command" in page
    assert "Path" in page


def test_send_page(request_handler: RequestHandler, mock_socket: MockSocket) -> None:
    """Test that send_page correctly sends HTTP headers and content."""
    # Given
    test_page = "<html><body>Test</body></html>"

    # When
    request_handler.send_page(test_page)

    # Then
    sent_data = mock_socket.buffer.getvalue().decode("utf-8")
    assert "HTTP/1.0 200 OK" in sent_data
    assert "Content-type: text/html" in sent_data
    assert "Content-Length: 30" in sent_data
    assert test_page in sent_data


def test_do_get(request_handler: RequestHandler, mock_socket: MockSocket) -> None:
    """Test the complete GET request handling process."""
    # When
    request_handler.do_GET()

    # Then
    sent_data = mock_socket.buffer.getvalue().decode("utf-8")
    assert "HTTP/1.0 200 OK" in sent_data
    assert "Content-type: text/html" in sent_data
    assert "<html>" in sent_data
    assert "<body>" in sent_data
    assert "<table>" in sent_data
    assert "127.0.0.1" in sent_data  # client host
    assert "12345" in sent_data  # client port
    assert "GET" in sent_data  # command
    assert "/" in sent_data  # path


if __name__ == "__main__":
    pytest.main()
