FROM mcr.microsoft.com/cbl-mariner/base/python:3.9

WORKDIR /app
COPY simple_server/payload.py payload.py
RUN alias python=python3
CMD ["python", "payload.py"]