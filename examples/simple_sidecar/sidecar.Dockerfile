FROM mcr.microsoft.com/cbl-mariner/base/python:3.9

WORKDIR /app
COPY simple_sidecar/sidecar_payload.py payload.py
CMD ["python3", "payload.py"]