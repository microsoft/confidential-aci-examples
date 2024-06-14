using './sidecar.bicep'

// Image info
param registry=''
param tag=''

// Deployment info
param location=''
param ccePolicies={
  sidecar: ''
}
param managedIDName=''
