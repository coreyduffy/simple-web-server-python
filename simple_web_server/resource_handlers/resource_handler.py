from abc import ABC, abstractmethod

# Import RequestHandler for type hinting in handle method
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from simple_web_server.__main__ import RequestHandler


class ResourceHandler(ABC):
    """
    Abstract Base Class for resource handlers.

    Defines the interface for checking if a path can be handled
    and handling the request for that path using the main RequestHandler.
    """

    @abstractmethod
    def can_handle(self, full_path: str) -> bool:
        """Check if this handler is appropriate for the given path."""
        pass

    @abstractmethod
    def handle(self, request_handler: "RequestHandler", full_path: str) -> None:
        """Process the request for the resource at the given path.

        Args:
            request_handler: The main SimpleWebServer.RequestHandler instance.
            full_path: The full absolute path to the resource.
        """
        pass
