FROM mcr.microsoft.com/devcontainers/base:bullseye

RUN pip install -r infra/requirements.txt
RUN curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
RUN az extension add --name confcom
