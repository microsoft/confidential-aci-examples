FROM mcr.microsoft.com/devcontainers/universal:linux

# Install Linux dependencies
RUN sudo apt-get update && sudo apt-get upgrade -y && sudo apt-get install -y cryptsetup

# Install Azure CLI
RUN curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Clone microsoft/hcsshim and setup
WORKDIR /home/vscode
RUN git clone https://github.com/microsoft/hcsshim.git
# RUN git clone git@ssh.dev.azure.com:v3/msazure/ContainerPlatform/containerd.cri