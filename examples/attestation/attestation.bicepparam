using './attestation.bicep'

// Image info
param registry='caciexamples.azurecr.io'
param tag=''

// Deployment info
param location=''
param ccePolicies={
  attestation: ''
}
param managedIDName='caciexamples'
