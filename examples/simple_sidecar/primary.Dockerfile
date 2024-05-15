FROM mcr.microsoft.com/cbl-mariner/base/python:3.9

WORKDIR /app
COPY simple_sidecar/primary_payload.py payload.py
RUN pip install requests
CMD ["python3", "payload.py"]