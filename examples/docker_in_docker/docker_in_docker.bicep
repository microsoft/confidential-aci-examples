param location string
param registry string
param ccePolicies object
param managedIDGroup string = resourceGroup().name
param managedIDName string

resource docker_in_docker 'Microsoft.ContainerInstance/containerGroups@2023-05-01' = {
    name: deployment().name
    location: location
    identity: {
      type: 'UserAssigned'
      userAssignedIdentities: {
        '${resourceId(managedIDGroup, 'Microsoft.ManagedIdentity/userAssignedIdentities', managedIDName)}': {}
      }
    }
    properties: {
      osType: 'Linux'
      sku: 'Confidential'
      restartPolicy: 'Never'
      confidentialComputeProperties: {
        ccePolicy: ccePolicies.docker_in_docker
      }
      imageRegistryCredentials: [
        {
          server: registry
          identity: resourceId(managedIDGroup, 'Microsoft.ManagedIdentity/userAssignedIdentities', managedIDName)
        }
      ]
      containers: [
        {
            name: 'docker-in-docker'
            properties: {
                image: '${registry}/docker:dind'
                environmentVariables: [
                    {
                        name: 'DOCKER_HOST'
                        value: 'unix:///var/run/docker.sock'
                    }
                ]
                securityContext: {
                  privileged: true
                }
                resources: {
                    requests: {
                        cpu: 1
                        memoryInGB: 4
                    }
                }
                command: [
                    'sh', '-c'
                    join([
                      'dockerd-entrypoint.sh --host=unix:///var/run/docker.sock & '
                      'while ! docker info &>/dev/null; do sleep 1; done && '
                      'docker run mcr.microsoft.com/mcr/hello-world:latest || true && '
                      'sleep infinity'
                    ], ' ')
                ]
            }
        }
      ]
    }
}

output ids array = [docker_in_docker.id]
