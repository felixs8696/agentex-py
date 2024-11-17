FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    htop \
    vim \
    curl \
    tar \
    python3-dev \
    postgresql-client \
    build-essential \
    libpq-dev \
    gcc \
    netcat-openbsd \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install tctl (Temporal CLI)
RUN curl -L https://github.com/temporalio/tctl/releases/download/v1.18.1/tctl_1.18.1_linux_arm64.tar.gz -o /tmp/tctl.tar.gz && \
    tar -xzf /tmp/tctl.tar.gz -C /usr/local/bin && \
    chmod +x /usr/local/bin/tctl && \
    rm /tmp/tctl.tar.gz

# Copy the requirements file
COPY agentex-py /app/agentex-py

WORKDIR /app/agentex-py/examples/agents/doc_writer

# Install the required Python packages
RUN pip install --ignore-installed -r requirements.txt

WORKDIR /app/agentex-py/examples/agents/doc_writer/project

# Run the FastAPI app
CMD ["python", "-m", "run_worker"]
