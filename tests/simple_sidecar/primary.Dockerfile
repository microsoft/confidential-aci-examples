FROM python:latest
WORKDIR /app
COPY simple_sidecar/primary_payload.py payload.py
RUN pip install requests
CMD ["python", "payload.py"]