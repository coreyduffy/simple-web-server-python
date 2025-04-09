import os
import tempfile
from unittest.mock import MagicMock

import pytest

from simple_web_server.resource_handlers.file_handler import FileHandler

# Tests will automatically use fixtures from ../conftest.py


class TestFileHandler:
    """Tests for the FileHandler."""

    @pytest.fixture
    def handler(self) -> FileHandler:
        """Fixture to provide a handler instance for tests."""
        return FileHandler()

    def test_can_handle_file(self, handler: FileHandler, temp_file: str) -> None:
        """Test can_handle returns True for files."""
        # Given (path from fixture)

        # When-Then
        assert handler.can_handle(temp_file) is True

    def test_cannot_handle_directory_or_non_existent(
        self, handler: FileHandler, temp_dir: str
    ) -> None:
        """Test can_handle returns False for directories or non-existent paths."""
        # Given
        non_existent_path = "/this/path/does/not/exist/ever"

        # When-Then
        assert handler.can_handle(temp_dir) is False
        assert handler.can_handle(non_existent_path) is False

    def test_handle_sends_file_content(
        self,
        handler: FileHandler,
        mock_request_handler: MagicMock,
        temp_file: str,
    ) -> None:
        """Test handle sends correct file content and headers."""
        # Given
        file_name = os.path.basename(temp_file)
        mock_request_handler.path = f"/{file_name}"

        # When
        handler.handle(mock_request_handler, temp_file)

        # Then
        # Check response headers
        mock_request_handler.send_response.assert_called_once_with(200)
        mock_request_handler.send_header.assert_any_call(
            "Content-type", "text/html"
        )  # Based on .html suffix
        mock_request_handler.send_header.assert_any_call("Content-Length", "38")
        mock_request_handler.end_headers.assert_called_once()

        # Check response body content
        assert (
            mock_request_handler.wfile.getvalue()
            == b"<html><body>Test content</body></html>"
        )

    def test_handle_unknown_content_type(
        self, handler: FileHandler, mock_request_handler: MagicMock
    ) -> None:
        """Test handle uses default content type for unknown file extensions."""
        # Given
        # Create a temp file with no common extension
        with tempfile.NamedTemporaryFile(delete=False, suffix=".unknownext") as f:
            f.write(b"dummy data")
            temp_file_unknown = f.name
        mock_request_handler.path = "/file.unknownext"

        try:
            # When
            handler.handle(mock_request_handler, temp_file_unknown)

            # Then
            # Check Content-type header used the default
            mock_request_handler.send_header.assert_any_call(
                "Content-type", "application/octet-stream"
            )
        finally:
            # Cleanup
            os.unlink(temp_file_unknown)

    def test_handle_file_read_error(
        self, handler: FileHandler, mock_request_handler: MagicMock
    ) -> None:
        """Test handle sends 404 on IOError reading file."""
        # Given
        non_existent_file = "/non/existent/file.txt"
        mock_request_handler.path = "/file.txt"
        # Note: We don't need to mock open directly, as open() will raise IOError
        # if the file doesn't exist, which is caught by the handler.

        # When
        handler.handle(mock_request_handler, non_existent_file)

        # Then
        mock_request_handler.send_error.assert_called_once()
        args, _ = mock_request_handler.send_error.call_args
        assert args[0] == 404  # Expecting 404 as per handler's exception handling
        assert "Could not read file" in args[1]
