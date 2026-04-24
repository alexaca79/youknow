targetScope = 'resourceGroup'

param environmentName string
param location string = resourceGroup().location
param tags object = {}

param speechVoice string = 'en-US-Grant:MAI-Voice-1'

var resourceSuffix = take(uniqueString(subscription().id, environmentName, location), 6)

// ── Built-in RBAC role IDs ──
var cognitiveServicesOpenAIUserRoleId = '5e0bd9bd-7b93-4f28-af87-19fc36ad61bd'
var cognitiveServicesSpeechUserRoleId = 'f2dc8367-1007-4938-bd23-fe263f013447'
var acrPullRoleId = '7f951dda-4ed3-4680-a7ca-43fe172d538d'

// ── User-Assigned Managed Identity ──
resource backendIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: 'id-backend-${environmentName}-${resourceSuffix}'
  location: location
  tags: tags
}

// ── Azure AI Foundry (AIServices account — OpenAI) ──
resource aiFoundry 'Microsoft.CognitiveServices/accounts@2025-06-01' = {
  name: 'ai-${environmentName}-${resourceSuffix}'
  location: location
  tags: tags
  kind: 'AIServices'
  sku: { name: 'S0' }
  identity: { type: 'SystemAssigned' }
  properties: {
    customSubDomainName: 'ai-${environmentName}-${resourceSuffix}'
    publicNetworkAccess: 'Enabled'
    disableLocalAuth: true
    allowProjectManagement: true
  }
}

// ── Model Deployment: gpt-4o-mini ──
resource gptDeployment 'Microsoft.CognitiveServices/accounts/deployments@2025-04-01-preview' = {
  parent: aiFoundry
  name: 'gpt-4o-mini'
  sku: {
    name: 'GlobalStandard'
    capacity: 10
  }
  properties: {
    model: {
      format: 'OpenAI'
      name: 'gpt-4o-mini'
      version: '2024-07-18'
    }
  }
}

// ── Azure Speech Service ──
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

// ── RBAC: Backend identity → Cognitive Services OpenAI User on AI Foundry ──
resource openaiRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(aiFoundry.id, backendIdentity.id, cognitiveServicesOpenAIUserRoleId)
  scope: aiFoundry
  properties: {
    principalId: backendIdentity.properties.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', cognitiveServicesOpenAIUserRoleId)
  }
}

// ── RBAC: Backend identity → Cognitive Services Speech User on Speech ──
resource speechRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(speech.id, backendIdentity.id, cognitiveServicesSpeechUserRoleId)
  scope: speech
  properties: {
    principalId: backendIdentity.properties.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', cognitiveServicesSpeechUserRoleId)
  }
}

// ── Container Registry ──
resource acr 'Microsoft.ContainerRegistry/registries@2023-07-01' = {
  name: 'cr${replace(environmentName, '-', '')}${resourceSuffix}'
  location: location
  tags: tags
  sku: { name: 'Basic' }
  properties: {
    adminUserEnabled: false
  }
}

// ── RBAC: Backend identity → AcrPull on ACR ──
resource acrPullBackend 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(acr.id, backendIdentity.id, acrPullRoleId)
  scope: acr
  properties: {
    principalId: backendIdentity.properties.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', acrPullRoleId)
  }
}

// ── Log Analytics ──
resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: 'log-${environmentName}-${resourceSuffix}'
  location: location
  tags: tags
  properties: {
    sku: { name: 'PerGB2018' }
    retentionInDays: 30
  }
}

// ── Container Apps Environment ──
resource containerEnv 'Microsoft.App/managedEnvironments@2024-03-01' = {
  name: 'cae-${environmentName}-${resourceSuffix}'
  location: location
  tags: tags
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: logAnalytics.properties.customerId
        sharedKey: logAnalytics.listKeys().primarySharedKey
      }
    }
  }
}

// ── Backend Container App ──
resource backendApp 'Microsoft.App/containerApps@2024-03-01' = {
  name: 'ca-backend-${resourceSuffix}'
  location: location
  tags: union(tags, { 'azd-service-name': 'backend' })
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${backendIdentity.id}': {}
    }
  }
  properties: {
    managedEnvironmentId: containerEnv.id
    configuration: {
      activeRevisionsMode: 'Single'
      ingress: {
        external: true
        targetPort: 8000
        transport: 'http'
        allowInsecure: false
      }
      registries: [
        {
          server: acr.properties.loginServer
          identity: backendIdentity.id
        }
      ]
    }
    template: {
      containers: [
        {
          name: 'backend'
          image: '${acr.properties.loginServer}/backend:latest'
          resources: {
            cpu: json('0.5')
            memory: '1Gi'
          }
          env: [
            { name: 'AZURE_CLIENT_ID', value: backendIdentity.properties.clientId }
            { name: 'OPENAI_BASE_URL', value: '${aiFoundry.properties.endpoint}openai/v1' }
            { name: 'OPENAI_MODEL', value: gptDeployment.name }
            { name: 'AZURE_SPEECH_ENDPOINT', value: speech.properties.endpoint }
            { name: 'AZURE_RESOURCE_ID', value: speech.id }
            { name: 'AZURE_SPEECH_VOICE', value: speechVoice }
            { name: 'FRONTEND_ORIGIN', value: '*' }
          ]
        }
      ]
      scale: {
        minReplicas: 0
        maxReplicas: 3
        rules: [
          {
            name: 'http-scaling'
            http: {
              metadata: {
                concurrentRequests: '50'
              }
            }
          }
        ]
      }
    }
  }
  dependsOn: [
    openaiRoleAssignment
    speechRoleAssignment
    acrPullBackend
  ]
}

output containerRegistryEndpoint string = acr.properties.loginServer
output containerRegistryName string = acr.name
output backendUrl string = 'https://${backendApp.properties.configuration.ingress.fqdn}'
output aiFoundryEndpoint string = aiFoundry.properties.endpoint
output aiFoundryResourceId string = aiFoundry.id
output speechEndpoint string = speech.properties.endpoint
output speechResourceId string = speech.id
