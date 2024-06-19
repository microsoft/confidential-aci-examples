FROM python:latest
WORKDIR /app
RUN pip install flask
COPY get_attestation.py payload.py /app/
CMD ["python", "payload.py"]