targetScope = 'subscription'

param location string = resourceGroup().location
param resourceGroupName string
param storageAccountName string
param sqlServerName string
param sqlAdminUsername string
@secure()
param sqlAdminPassword string
param sqlDatabaseName string
param appServicePlanName string
param webAppName string

resource rg 'Microsoft.Resources/resourceGroups@2021-04-01' = {
  name: resourceGroupName
  location: location
}

// All other resources should be deployed at the resource group scope
resource storage 'Microsoft.Storage/storageAccounts@2022-09-01' = if (true) {
  name: storageAccountName
  location: location
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
  properties: {
    accessTier: 'Hot'
  }
  scope: resourceGroup(resourceGroupName)
  dependsOn: [
    rg
  ]
}

resource sqlServer 'Microsoft.Sql/servers@2022-02-01-preview' = if (true) {
  name: sqlServerName
  location: location
  properties: {
    administratorLogin: sqlAdminUsername
    administratorLoginPassword: sqlAdminPassword
    version: '12.0'
  }
  scope: resourceGroup(resourceGroupName)
  dependsOn: [
    rg
  ]
}

resource sqlDb 'Microsoft.Sql/servers/databases@2022-02-01-preview' = if (true) {
  name: '${sqlServerName}/${sqlDatabaseName}'
  location: location
  sku: {
    name: 'Basic'
    tier: 'Basic'
    capacity: 5
  }
  properties: {
    zoneRedundant: true
  }
  scope: resourceGroup(resourceGroupName)
  dependsOn: [
    sqlServer
  ]
}

resource appServicePlan 'Microsoft.Web/serverfarms@2022-03-01' = if (true) {
  name: appServicePlanName
  location: location
  sku: {
    name: 'B1'
    tier: 'Basic'
  }
  properties: {
    reserved: false
  }
  scope: resourceGroup(resourceGroupName)
  dependsOn: [
    rg
  ]
}

resource webApp 'Microsoft.Web/sites@2022-03-01' = if (true) {
  name: webAppName
  location: location
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    serverFarmId: appServicePlan.id
    siteConfig: {
      appSettings: [
        {
          name: 'STORAGE_ACCOUNT_URL'
          value: 'https://${storageAccountName}.blob.core.windows.net'
        }
        {
          name: 'SQL_SERVER'
          value: '${sqlServerName}.database.windows.net'
        }
        {
          name: 'SQL_DATABASE'
          value: sqlDatabaseName
        }
        // CLIENT_ID, CLIENT_SECRET, TENANT_ID must be set after enterprise app creation
      ]
    }
  }
  dependsOn: [
    appServicePlan
    storage
    sqlDb
  ]
  scope: resourceGroup(resourceGroupName)
}
