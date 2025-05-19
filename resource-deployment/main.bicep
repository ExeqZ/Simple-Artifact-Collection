targetScope = 'subscription'

param location string = 'westeurope'
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

module rgResources 'rg-resources.bicep' = {
  name: 'rgResourcesDeployment'
  scope: resourceGroup(resourceGroupName)
  params: {
    location: location
    storageAccountName: storageAccountName
    sqlServerName: sqlServerName
    sqlAdminUsername: sqlAdminUsername
    sqlAdminPassword: sqlAdminPassword
    sqlDatabaseName: sqlDatabaseName
    appServicePlanName: appServicePlanName
    webAppName: webAppName
  }
  dependsOn: [
    rg
  ]
}
