FROM python:latest
WORKDIR /app
COPY simple_sidecar/sidecar_payload.py payload.py
CMD ["python", "payload.py"]