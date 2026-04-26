param environmentName string
param location string
param tags object
param resourceSuffix string

resource backendIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: 'id-backend-${environmentName}-${resourceSuffix}'
  location: location
  tags: tags
}

output identityId string = backendIdentity.id
output principalId string = backendIdentity.properties.principalId
output clientId string = backendIdentity.properties.clientId
