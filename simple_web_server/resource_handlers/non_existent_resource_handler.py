import os
from typing import TYPE_CHECKING

# Import the base class
from .resource_handler import ResourceHandler

if TYPE_CHECKING:
    from simple_web_server.__main__ import RequestHandler


class NonExistentResourceHandler(ResourceHandler):
    """
    Handles requests for resources that do not exist on the filesystem.
    Sends a 404 error response.
    """

    def can_handle(self, full_path: str) -> bool:
        """Handle if the path does not exist."""
        return not os.path.exists(full_path)

    def handle(self, request_handler: "RequestHandler", full_path: str) -> None:
        """Send a 404 error using the main request handler."""
        request_handler.send_error(
            404, f"File/Directory not found: {request_handler.path}"
        )
