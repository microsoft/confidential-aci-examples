FROM mcr.microsoft.com/devcontainers/base:bullseye

RUN apt-get update && apt-get install -y python3 python3-pip
COPY infra/requirements.txt .
RUN pip install -r requirements.txt
RUN curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
RUN az extension add --name confcom
