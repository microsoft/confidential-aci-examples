FROM python:latest
WORKDIR /app
COPY primary_payload.py payload.py
RUN pip install requests
CMD ["python", "payload.py"]