# Use a lightweight Python image
FROM python:3.12-slim

# Set up the working directory
WORKDIR /app

RUN pip install uvicorn

# Copy the requirements file
COPY agentex-py /app/agentex-py

WORKDIR /app/agentex-py/examples/agents/doc_writer

# Install the required Python packages
RUN pip install --ignore-installed -r requirements.txt

WORKDIR /app/agentex-py/examples/agents/doc_writer/project

# Set the entrypoint to run FastAPI using Uvicorn
CMD ["uvicorn", "main:agent.app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
