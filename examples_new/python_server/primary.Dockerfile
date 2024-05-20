FROM python:latest
WORKDIR /app
COPY payload.py payload.py
CMD ["python", "payload.py"]