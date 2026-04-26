param environmentName string
param location string
param tags object
param resourceSuffix string
param backendIdentityId string
param backendPrincipalId string

var cognitiveServicesSpeechUserRoleId = 'f2dc8367-1007-4938-bd23-fe263f013447'

resource speech 'Microsoft.CognitiveServices/accounts@2025-06-01' = {
  name: 'speech-${environmentName}-${resourceSuffix}'
  location: location
  tags: tags
  kind: 'SpeechServices'
  sku: { name: 'S0' }
  identity: { type: 'SystemAssigned' }
  properties: {
    customSubDomainName: 'speech-${environmentName}-${resourceSuffix}'
    publicNetworkAccess: 'Enabled'
    disableLocalAuth: true
  }
}

resource speechRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(speech.id, backendIdentityId, cognitiveServicesSpeechUserRoleId)
  scope: speech
  properties: {
    principalId: backendPrincipalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', cognitiveServicesSpeechUserRoleId)
  }
}

output endpoint string = speech.properties.endpoint
output resourceId string = speech.id
