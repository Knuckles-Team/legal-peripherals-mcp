FROM python:3.11-slim

WORKDIR /app
COPY . .
RUN pip install -e .[all]

ENTRYPOINT ["python", "-m", "legal_peripherals_mcp.mcp_server"]
