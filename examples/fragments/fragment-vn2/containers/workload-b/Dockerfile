FROM mcr.microsoft.com/mirror/docker/library/ubuntu:24.04

RUN apt-get update && apt-get install -y python3 python3-fastapi uvicorn

COPY workload_server.py .

CMD ["python3", "workload_server.py"]
