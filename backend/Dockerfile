# Builder Stage
FROM python:3.11-slim as builder

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /src

# Install necessary build dependencies, xmlsec1 and pipenv
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    pkg-config \
    libxml2-dev \
    libxmlsec1-dev \
    libxmlsec1-openssl \
    xmlsec1 \
    libmagic1 \
    && pip install pipenv==2023.12.1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy Pipfile and lockfile for dependency installation
COPY Pipfile Pipfile.lock /src/

# Install dependencies into the system environment
RUN pipenv install --system --dev --deploy

# Runtime Stage
FROM python:3.11-slim

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install xmlsec1 runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libxml2 \
    libxmlsec1 \
    libxmlsec1-openssl \
    xmlsec1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /src

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy the application code
COPY . /src/

# Expose the application port
EXPOSE 8001

# Set the default command
CMD ["uvicorn", "pawprints.main:app", "--host", "0.0.0.0", "--port", "8001"]
