import http.server
import os


class RequestHandler(http.server.BaseHTTPRequestHandler):
    """
    Handle GET requests by returning a fixed HTML page.
    """

    def do_GET(self) -> None:
        try:
            full_path = os.getcwd() + self.path
            if not os.path.exists(full_path):
                self.send_error(404, f"File not found: {full_path}")
            else:
                self.send_file(full_path)
        except Exception as e:
            self.send_error(404, str(e))

    def send_file(self, full_path: str) -> None:
        try:
            with open(full_path, "rb") as file:
                content = file.read()
                self.send_content(content)
        except Exception as e:
            raise Exception(f"Error reading file: {e}") from e

    def send_content(self, content: bytes) -> None:
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)


if __name__ == "__main__":
    server_address = ("", 8080)
    server = http.server.HTTPServer(server_address, RequestHandler)
    server.serve_forever()
