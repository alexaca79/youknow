targetScope = 'resourceGroup'

@minLength(1)
@maxLength(64)
param environmentName string

@minLength(1)
param location string = resourceGroup().location

param speechVoice string = 'en-US-Grant:MAI-Voice-1'

var tags = { 'azd-env-name': environmentName }

module resources './modules/resources.bicep' = {
  name: 'resources'
  params: {
    environmentName: environmentName
    location: location
    tags: tags
    speechVoice: speechVoice
  }
}

output AZURE_CONTAINER_REGISTRY_ENDPOINT string = resources.outputs.containerRegistryEndpoint
output AZURE_CONTAINER_REGISTRY_NAME string = resources.outputs.containerRegistryName
output WEB_URL string = resources.outputs.backendUrl
output AZURE_AI_FOUNDRY_ENDPOINT string = resources.outputs.aiFoundryEndpoint
output AZURE_AI_FOUNDRY_RESOURCE_ID string = resources.outputs.aiFoundryResourceId
output AZURE_SPEECH_ENDPOINT string = resources.outputs.speechEndpoint
output AZURE_SPEECH_RESOURCE_ID string = resources.outputs.speechResourceId
