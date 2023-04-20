FROM python:latest
WORKDIR /app
COPY primary_payload.py payload.py
CMD ["python", "payload.py"]