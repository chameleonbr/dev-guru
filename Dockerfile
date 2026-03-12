# Use a multi-stage build to keep the final image small
FROM python:3.13-slim AS builder

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set the working directory
WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy only requirements first to leverage Docker cache
COPY pyproject.toml uv.lock ./

# Install dependencies using uv
# --no-install-project ensures we don't try to install the app yet
RUN uv sync --frozen --no-install-project --no-dev

# Final stage
FROM python:3.13-slim

WORKDIR /app

# Copy the virtual environment from the builder
COPY --from=builder /app/.venv /app/.venv

# Add virtualenv to PATH
ENV PATH="/app/.venv/bin:$PATH"

# Copy the source code
COPY . .

# Ensure skills directory exists
RUN mkdir -p skills

# Expose the API port
EXPOSE 8000

# Set environment variables
ENV PYTHONPATH=.
ENV PYTHONUNBUFFERED=1

# Command to run the application
CMD ["python", "main.py"]
