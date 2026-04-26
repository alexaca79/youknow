targetScope = 'resourceGroup'

param environmentName string
param location string = resourceGroup().location
param tags object = {}

param speechVoice string = 'en-US-Grant:MAI-Voice-1'

var resourceSuffix = take(uniqueString(subscription().id, environmentName, location), 6)

// ── Managed Identity ──
module identity './identity.bicep' = {
  name: 'identity'
  params: {
    environmentName: environmentName
    location: location
    tags: tags
    resourceSuffix: resourceSuffix
  }
}

// ── AI Foundry (OpenAI) ──
module aiFoundry './ai-foundry.bicep' = {
  name: 'ai-foundry'
  params: {
    environmentName: environmentName
    location: location
    tags: tags
    resourceSuffix: resourceSuffix
    backendIdentityId: identity.outputs.identityId
    backendPrincipalId: identity.outputs.principalId
  }
}

// ── Speech Service ──
module speech './speech.bicep' = {
  name: 'speech'
  params: {
    environmentName: environmentName
    location: location
    tags: tags
    resourceSuffix: resourceSuffix
    backendIdentityId: identity.outputs.identityId
    backendPrincipalId: identity.outputs.principalId
  }
}

// ── Container Registry ──
module acr './container-registry.bicep' = {
  name: 'container-registry'
  params: {
    environmentName: environmentName
    location: location
    tags: tags
    resourceSuffix: resourceSuffix
    backendIdentityId: identity.outputs.identityId
    backendPrincipalId: identity.outputs.principalId
  }
}

// ── Container Apps (environment + backend app) ──
module containerApps './container-apps.bicep' = {
  name: 'container-apps'
  params: {
    environmentName: environmentName
    location: location
    tags: tags
    resourceSuffix: resourceSuffix
    backendIdentityId: identity.outputs.identityId
    backendClientId: identity.outputs.clientId
    acrLoginServer: acr.outputs.loginServer
    acrIdentityId: acr.outputs.identityId
    aiFoundryEndpoint: aiFoundry.outputs.endpoint
    modelDeploymentName: aiFoundry.outputs.modelDeploymentName
    speechEndpoint: speech.outputs.endpoint
    speechResourceId: speech.outputs.resourceId
    speechVoice: speechVoice
  }
}

output containerRegistryEndpoint string = acr.outputs.loginServer
output containerRegistryName string = acr.outputs.name
output backendUrl string = containerApps.outputs.backendUrl
output aiFoundryEndpoint string = aiFoundry.outputs.endpoint
output aiFoundryResourceId string = aiFoundry.outputs.resourceId
output speechEndpoint string = speech.outputs.endpoint
output speechResourceId string = speech.outputs.resourceId
