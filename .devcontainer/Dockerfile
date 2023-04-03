FROM mcr.microsoft.com/devcontainers/universal:linux

# Install Azure CLI
RUN curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
RUN az extension add --name confcom

# Clone microsoft/hcsshim and setup
WORKDIR /home/vscode
RUN git clone https://github.com/microsoft/hcsshim.git
# RUN git clone git@ssh.dev.azure.com:v3/msazure/ContainerPlatform/containerd.cri