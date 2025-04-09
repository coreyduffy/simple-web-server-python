import os
import tempfile
from unittest.mock import MagicMock

import pytest

from simple_web_server.resource_handlers.non_existent_resource_handler import (
    NonExistentResourceHandler,
)

# Tests will automatically use fixtures from ../conftest.py


class TestNonExistentResourceHandler:
    """Tests for the NonExistentResourceHandler."""

    @pytest.fixture
    def handler(self) -> NonExistentResourceHandler:
        """Fixture to provide a handler instance for tests."""
        return NonExistentResourceHandler()

    def test_can_handle_non_existent(self, handler: NonExistentResourceHandler) -> None:
        """Test can_handle returns True for paths that do not exist."""
        # Given
        # Create and delete file/dir to get paths that definitely don't exist
        temp_f = tempfile.NamedTemporaryFile(delete=False)
        existent_file_path = temp_f.name
        temp_f.close()
        os.unlink(existent_file_path)

        existent_dir_path = tempfile.mkdtemp()
        os.rmdir(existent_dir_path)

        truly_non_existent_path = "/this/path/absolutely/does/not/exist/12345"

        # When-Then (Paths do NOT exist -> can_handle should be TRUE)
        assert handler.can_handle(truly_non_existent_path) is True
        assert handler.can_handle(existent_file_path) is True
        assert handler.can_handle(existent_dir_path) is True

    def test_cannot_handle_existent(
        self,
        handler: NonExistentResourceHandler,
        temp_file: str,
        temp_dir: str,
    ) -> None:
        """Test can_handle returns False for paths that DO exist."""
        # Given (paths from fixtures)

        # When-Then (Paths DO exist -> can_handle should be FALSE)
        assert handler.can_handle(temp_file) is False
        assert handler.can_handle(temp_dir) is False

    def test_handle_sends_404(
        self,
        handler: NonExistentResourceHandler,
        mock_request_handler: MagicMock,
    ) -> None:
        """Test handle calls send_error with 404."""
        # Given
        test_path = "/some/non_existent/path"
        mock_request_handler.path = test_path
        absolute_path = "/absolute" + test_path

        # When
        handler.handle(mock_request_handler, absolute_path)

        # Then
        mock_request_handler.send_error.assert_called_once_with(
            404, f"File/Directory not found: {test_path}"
        )
