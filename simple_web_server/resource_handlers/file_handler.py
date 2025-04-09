import mimetypes  # For guessing content type
import os
from typing import TYPE_CHECKING

from .resource_handler import ResourceHandler

if TYPE_CHECKING:
    from simple_web_server.__main__ import RequestHandler


class FileHandler(ResourceHandler):
    """
    Handles requests for existing files on the filesystem.
    Determines content type and sends the file content.
    """

    def can_handle(self, full_path: str) -> bool:
        """Handle if the path is an existing file."""
        return os.path.isfile(full_path)

    def handle(self, request_handler: "RequestHandler", full_path: str) -> None:
        """Read the file and send its content with appropriate headers."""
        try:
            with open(full_path, "rb") as file:
                content = file.read()

            # Guess the content type
            ctype, encoding = mimetypes.guess_type(full_path)
            if ctype is None:
                ctype = "application/octet-stream"  # Default if type unknown

            # Send the response using the main request handler
            request_handler.send_response(200)
            request_handler.send_header("Content-type", ctype)
            request_handler.send_header("Content-Length", str(len(content)))
            request_handler.end_headers()
            request_handler.wfile.write(content)
        except OSError as e:
            request_handler.send_error(
                404, f"Could not read file: {request_handler.path}, Error: {e}"
            )  # Using 404 might be suitable if the file becomes inaccessible
        except Exception as e:
            request_handler.send_error(
                500, f"Error sending file: {request_handler.path}, Error: {e}"
            )
