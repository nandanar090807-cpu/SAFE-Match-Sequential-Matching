# SAFE-Match deterministic, build-network-independent inference image.
# Base image still must be pulled or available in the Docker host.
FROM python:3.11-slim
WORKDIR /app
COPY policy.py /app/policy.py
COPY requirements.txt /app/requirements.txt
COPY vendor/ /app/vendor/
ENV PYTHONPATH=/app/vendor PYTHONDONTWRITEBYTECODE=1
USER 65534:65534
ENTRYPOINT ["python", "-S", "/app/policy.py"]