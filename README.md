# Simple Web Server

A simple Python web server implementation.
The web server will return files that are found from the current director where the server is running.

## Running the server
You can run the server via the commands below from the project root directory:
```bash
python -m venv venv
source venv/bin/activate
pip install -e .
python simple_web_server
```

## Development Setup

1. Install the package in development mode with all dev dependencies:
```bash
pip install -e ".[dev]"
```

2. Run the tests:
```bash
pytest
```

3. Format code with Black:
```bash
black .
```

4. Run linting with Ruff:
```bash
ruff check .
```

5. Run type checking with mypy:
```bash
mypy .
```

## Development Tools

This project uses:
- [pytest](https://docs.pytest.org/) for testing
- [Black](https://black.readthedocs.io/) for code formatting
- [Ruff](https://beta.ruff.rs/docs/) for linting
- [mypy](https://mypy.readthedocs.io/) for static type checking

All tools are configured in `pyproject.toml`.
