FROM python:latest
WORKDIR /app
RUN pip install flask
COPY payload.py payload.py
CMD ["python", "payload.py"]