FROM python:latest
WORKDIR /app
COPY sidecar_payload.py payload.py
CMD ["python", "payload.py"]