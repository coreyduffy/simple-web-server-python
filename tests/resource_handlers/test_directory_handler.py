import os
from unittest.mock import ANY, MagicMock, patch

import pytest

from simple_web_server.resource_handlers.directory_handler import DirectoryHandler

# Tests will automatically use fixtures from ../conftest.py


class TestDirectoryHandler:
    """Tests for the DirectoryHandler."""

    @pytest.fixture
    def handler(self) -> DirectoryHandler:
        """Fixture to provide a handler instance for tests."""
        return DirectoryHandler()

    def test_can_handle_directory(
        self, handler: DirectoryHandler, temp_dir: str
    ) -> None:
        """Test can_handle returns True for directories."""
        # Given (path from fixture)

        # When-Then
        assert handler.can_handle(temp_dir) is True

    def test_cannot_handle_file_or_non_existent(
        self, handler: DirectoryHandler, temp_file: str
    ) -> None:
        """Test can_handle returns False for files or non-existent paths."""
        # Given
        non_existent_path = "/this/path/does/not/exist/ever"

        # When-Then
        assert handler.can_handle(temp_file) is False
        assert handler.can_handle(non_existent_path) is False

    def test_handle_sends_listing(
        self,
        handler: DirectoryHandler,
        mock_request_handler: MagicMock,
        temp_dir: str,
    ) -> None:
        """Test handle sends correct directory listing HTML."""
        # Given
        dir_name = os.path.basename(temp_dir)
        mock_request_handler.path = f"/{dir_name}/"

        # When
        handler.handle(mock_request_handler, temp_dir)

        # Then
        # Check response headers
        mock_request_handler.send_response.assert_called_once_with(200)
        mock_request_handler.send_header.assert_any_call(
            "Content-type", "text/html; charset=utf-8"
        )
        mock_request_handler.send_header.assert_any_call("Content-Length", ANY)
        mock_request_handler.end_headers.assert_called_once()

        # Check response body content
        written_data = mock_request_handler.wfile.getvalue()
        expected_title = f"Directory listing for /{dir_name}/"
        assert expected_title.encode() in written_data
        # Check for files/dirs present in the fixture
        assert b"file1.html" in written_data
        assert b"file2.txt" in written_data
        assert b"subdir/" in written_data  # Check directory link has trailing slash

    def test_handle_permission_error(
        self,
        handler: DirectoryHandler,
        mock_request_handler: MagicMock,
        temp_dir: str,
    ) -> None:
        """Test handle sends 403 on OSError (permission denied)."""
        # Given
        restricted_path_abs = os.path.join(temp_dir, "restricted")
        mock_request_handler.path = "/restricted/"
        # Mock os.listdir to raise PermissionError
        with patch(
            "os.listdir", side_effect=OSError("[Errno 13] Permission denied")
        ) as mock_listdir:
            # When
            handler.handle(mock_request_handler, restricted_path_abs)

            # Then
            mock_listdir.assert_called_once_with(restricted_path_abs)
            mock_request_handler.send_error.assert_called_once()
            args, _ = mock_request_handler.send_error.call_args
            assert args[0] == 403
            assert "Permission denied" in args[1]
