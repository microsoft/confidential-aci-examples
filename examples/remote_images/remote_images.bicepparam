using './remote_images.bicep'

// Image info
param registry=''

// Deployment info
param location=''
param ccePolicies={
  remote_images_alpine: ''
  remote_images_nginx: ''
  remote_images_python: ''
  remote_images_ubuntu: ''
}
param managedIDName='caciexamples'
