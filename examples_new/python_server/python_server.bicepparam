using './python_server.bicep'

// Image info
param registry=''
param tag=''

// Deployment info
param location=''
param ccePolicies={
  python_server: ''
}
param managedIDName=''
