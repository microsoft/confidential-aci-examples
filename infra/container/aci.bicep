@secure()
param manifest object
param registryUrl string
param location string = resourceGroup().location
param securityPolicies string
param tag string

resource containerGroups 'Microsoft.ContainerInstance/containerGroups@2023-05-01' = [for (group, groupIdx) in manifest.containerGroups: {
  name: '${deployment().name}-group-${groupIdx}'
  location: location
  tags: {
    Owner: 'c-aci-examples'
    GithubRepo: 'microsoft/c-aci-examples'
  }
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${resourceId('Microsoft.ManagedIdentity/userAssignedIdentities', 'caciexamples')}': {}
    }
  }
  properties: {
    osType: 'Linux'
    sku: 'Confidential'
    ipAddress: {
      type: 'Public'
      ports: map(group.ports, port => {
        protocol: 'TCP'
        ports: port
      })
    }
    volumes: map(group.volumes, volume => {
      name: volume
      emptyDir: {}
    })
    confidentialComputeProperties: {
      ccePolicy: base64('package${split(securityPolicies, 'package')[groupIdx]}')
    }
    imageRegistryCredentials: manifest.registryCredentials
    containers: [for (container, containerIdx) in group.containers: {
      name: '${deployment().name}-container-${containerIdx}'
      properties: {
        image: startsWith(container.image, 'http') ? split(container.image, '://')[1] : '${registryUrl}/${manifest.testName}/${container.image}:${tag}'
        ports: map(container.ports, port => {
          protocol: 'TCP'
          port: port
        })
        securityContext: {
          privileged: container.privileged ?? false
        }
        volumeMounts: map(container.mounts, mount => {
          name: mount.name
          mountPath: mount.mountPath
        })
        environmentVariables: container.env
        resources: {
          requests: {
            cpu: container.cores
            memoryInGB: container.ram
          }
        }
        command: container.command
      }
    }]
  }
}]
