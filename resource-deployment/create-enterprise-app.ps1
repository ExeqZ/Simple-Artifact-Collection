param(
    [string]$appName = "FileManagementSystemApp"
)

# Login to Azure
az login

# Create app registration
$app = az ad app create --display-name $appName | ConvertFrom-Json

# Create service principal
$sp = az ad sp create --id $app.appId | ConvertFrom-Json

# Create client secret
$secret = az ad app credential reset --id $app.appId --append --display-name "DefaultSecret" | ConvertFrom-Json

Write-Host "App Registration created:"
Write-Host "CLIENT_ID=$($app.appId)"
Write-Host "CLIENT_SECRET=$($secret.password)"
Write-Host "TENANT_ID=$((az account show --query tenantId -o tsv))"
