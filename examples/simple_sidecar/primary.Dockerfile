FROM mcr.microsoft.com/cbl-mariner/base/python:3.9

WORKDIR /app
COPY simple_sidecar/primary_payload.py payload.py
RUN pip install requests
RUN alias python=python3
CMD ["python", "payload.py"]