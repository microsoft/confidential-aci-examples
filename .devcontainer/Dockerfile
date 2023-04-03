FROM mcr.microsoft.com/devcontainers/universal:linux

# Install Azure CLI
RUN curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
RUN az extension add --name confcom

ARG SSH_KEY
RUN mkdir -p ~/.ssh
RUN echo "$SSH_KEY" | sed 's/-----.*-----//g; s/\n//g; s/ /\n/g' | sed '1s/^/-----BEGIN OPENSSH PRIVATE KEY-----/' | sed 'N;/^\n$/d;P;D' | sed '$s/$/\n-----END OPENSSH PRIVATE KEY-----\n/' > ~/.ssh/id_rsa
RUN chmod 600 ~/.ssh/id_rsa
RUN ssh-keygen -y -f ~/.ssh/id_rsa > ~/.ssh/id_rsa.pub

# Clone microsoft/hcsshim and setup
WORKDIR /home/vscode
RUN git clone https://github.com/microsoft/hcsshim.git
RUN git clone git@ssh.dev.azure.com:v3/msazure/ContainerPlatform/containerd.cri