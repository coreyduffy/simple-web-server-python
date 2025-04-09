import http.server
import os
from typing import ClassVar

from simple_web_server.resource_handlers.directory_handler import DirectoryHandler
from simple_web_server.resource_handlers.file_handler import FileHandler
from simple_web_server.resource_handlers.non_existent_resource_handler import (
    NonExistentResourceHandler,
)
from simple_web_server.resource_handlers.resource_handler import ResourceHandler


class RequestHandler(http.server.BaseHTTPRequestHandler):
    """
    Handle GET requests by returning a fixed HTML page.
    """

    resource_handler_classes: ClassVar[list[type[ResourceHandler]]] = [
        NonExistentResourceHandler,
        DirectoryHandler,
        FileHandler,
    ]

    def do_GET(self) -> None:
        try:
            full_path = os.getcwd() + self.path
            for handler_class in self.resource_handler_classes:
                handler_instance = handler_class()
                if handler_instance.can_handle(full_path):
                    handler_instance.handle(self, full_path)
                    return
            super().send_error(501, f"Unsupported resource type: {full_path}")
        except Exception as e:
            super().send_error(500, str(e))


if __name__ == "__main__":
    server_address = ("", 8080)
    server = http.server.HTTPServer(server_address, RequestHandler)
    server.serve_forever()
