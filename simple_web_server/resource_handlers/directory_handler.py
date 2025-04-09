import os
from typing import TYPE_CHECKING

from .resource_handler import ResourceHandler

if TYPE_CHECKING:
    from simple_web_server.__main__ import RequestHandler


class DirectoryHandler(ResourceHandler):
    """
    Handles requests for directories by listing their contents.
    """

    def can_handle(self, full_path: str) -> bool:
        """Handle if the path is a directory."""
        return os.path.isdir(full_path)

    def handle(self, request_handler: "RequestHandler", full_path: str) -> None:
        """Generate and send an HTML directory listing."""
        try:
            dir_contents = os.listdir(full_path)
            title = f"Directory listing for {request_handler.path}"
            page_parts = [
                f"<html><head><title>{title}</title></head>",
                f"<body><h1>{title}</h1><hr><ul>",
            ]
            for item in sorted(dir_contents):
                link_path = item
                if os.path.isdir(os.path.join(full_path, item)):
                    link_path += "/"  # Add trailing slash for directories
                page_parts.append(f"<li><a href='{link_path}'>{item}</a></li>")

            page_parts.append("</ul><hr></body></html>")
            html_content = "\n".join(page_parts)

            encoded_content = html_content.encode("utf-8")
            request_handler.send_response(200)
            request_handler.send_header("Content-type", "text/html; charset=utf-8")
            request_handler.send_header("Content-Length", str(len(encoded_content)))
            request_handler.end_headers()
            request_handler.wfile.write(encoded_content)
        except OSError as e:
            error_msg = (
                f"Permission denied accessing directory: {request_handler.path}, "
                f"Error: {e}"
            )
            request_handler.send_error(403, error_msg)
        except Exception as e:
            error_msg = f"Error listing directory: {request_handler.path}, Error: {e}"
            request_handler.send_error(500, error_msg)
