param location string
param registry string
param ccePolicies object
param managedIDGroup string = resourceGroup().name
param managedIDName string

var images = [
  'alpine:latest'
  'nginx:stable'
  'ubuntu:latest'
  'python:latest'
]

resource containerGroups 'Microsoft.ContainerInstance/containerGroups@2023-05-01' = [for (image, i) in images: {
  name: '${deployment().name}-${first(split(image, ':'))}'
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
      ccePolicy: ccePolicies['remote_images_${first(split(image, ':'))}']
    }
    imageRegistryCredentials: [
      {
        server: registry
        identity: resourceId(managedIDGroup, 'Microsoft.ManagedIdentity/userAssignedIdentities', managedIDName)
      }
    ]
    containers: [
      {
        name: 'primary'
        properties: {
          image: image
          ports: []
          resources: {
            requests: {
              memoryInGB: 4
              cpu: 1
            }
          }
          command: ['sleep', '1']
        }
      }
    ]
  }
}]

output ids array = [
  containerGroups[0].id
  containerGroups[1].id
  containerGroups[2].id
  containerGroups[3].id
]
