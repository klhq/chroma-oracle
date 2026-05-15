# Use specific version for stability
FROM python:3.13-slim-bookworm

# Copy uv from the official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Copy dependency definitions
COPY pyproject.toml uv.lock ./

# Install dependencies using uv (without project code for caching)
RUN uv export --frozen --no-dev -o /tmp/requirements.txt && \
    uv pip install --system --no-cache -r /tmp/requirements.txt && \
    rm /tmp/requirements.txt

# Copy project files
COPY README.md ./
COPY chroma_oracle ./chroma_oracle
COPY levels ./levels

# Install the project itself
RUN uv pip install --system --no-cache --no-deps .

# Set the entrypoint to the application
ENTRYPOINT ["chroma-oracle"]

# Default argument
CMD ["--help"]
