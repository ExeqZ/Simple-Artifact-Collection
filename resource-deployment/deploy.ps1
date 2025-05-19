param(
    [string]$parametersFile = "./main.parameters.json"
)

# Login to Azure
az login

# Read parameters
$parameters = Get-Content $parametersFile | ConvertFrom-Json
$rgName = $parameters.parameters.resourceGroupName.value
$location = $parameters.parameters.location.value

# Create resource group
az group create --name $rgName --location $location

# Deploy Bicep template
az deployment group create `
  --resource-group $rgName `
  --template-file ./main.bicep `
  --parameters @$parametersFile
