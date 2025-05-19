# Azure Resource Deployment for File Management System

This directory contains all necessary Bicep templates and scripts to deploy the required Azure resources for the File Management System.

---

## Prerequisites

- **Azure Subscription** with sufficient permissions to create resources.
- **Azure CLI** installed ([Install Guide](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli)).
- **Bicep CLI** installed ([Install Guide](https://docs.microsoft.com/en-us/azure/azure-resource-manager/bicep/install)).
- **PowerShell** (for running deployment scripts).
- **ODBC Driver 17 for SQL Server** (for local development).

---

## Resources Deployed

- **Resource Group** (subscription scope)
- **Azure Storage Account** (StorageV2, general purpose v2)
- **Azure SQL Server & Database** (Basic, 5 DTU, zone redundant)
- **App Service Plan** (Basic B1, with Managed Identity)
- **Web App** (with Managed Identity)
- **Enterprise Application** (Azure AD App Registration)

---

## Deployment Steps

### 1. Configure Parameters

Edit `main.parameters.json` to set your desired resource names, admin credentials, and location.

### 2. Deploy Azure Resources

Run the deployment script from this directory:

```powershell
./deploy.ps1
```

This will:
- Create the resource group at the subscription scope
- Deploy all resources defined in `rg-resources.bicep` into that resource group using your parameters

### 3. Create Azure AD Enterprise Application

Run the script to create an Azure AD App Registration and Service Principal:

```powershell
./create-enterprise-app.ps1
```

This will output:
- `CLIENT_ID`
- `CLIENT_SECRET`
- `TENANT_ID`

**Save these values** for use as environment variables in the web app.

### 4. Assign Managed Identity Permissions

After deploying the resources and creating the Enterprise Application, you need to grant the correct permissions to your Web App's managed identity and the Enterprise App. This ensures secure access to the Storage Account and SQL Database.

#### a. Assign Storage Account Permissions

Grant the Web App's managed identity the **Storage Blob Data Contributor** role on the storage account:

```powershell
# Get the Web App's managed identity principal ID
$webAppName = "<your-web-app-name>"
$resourceGroupName = "<your-resource-group-name>"
$identity = az webapp identity show --name $webAppName --resource-group $resourceGroupName --query principalId -o tsv

# Assign the role
$storageAccountName = "<your-storage-account-name>"
az role assignment create --assignee $identity --role "Storage Blob Data Contributor" --scope $(az storage account show --name $storageAccountName --resource-group $resourceGroupName --query id -o tsv)
```

#### b. Assign SQL Database Permissions

Grant the managed identity access to the SQL Database. You must connect to the database and run SQL statements to create a login and a contained user, then assign it the necessary roles.

1. **Get the managed identity's object ID**:

```powershell
az webapp identity show --name <webAppName> --resource-group <resourceGroupName> --query principalId -o tsv
```

2. **Connect to the SQL Server** (master database) as the Azure SQL admin using Azure Data Studio, SSMS, or `sqlcmd`.

3. **Create a login for the managed identity** (in the master database):

```sql
CREATE LOGIN [<web-app-msi-object-id>] FROM EXTERNAL PROVIDER;
```

4. **Create a user in the application database and assign roles**:

```sql
-- Connect to your application database (e.g., CaseManagementDB)
USE [CaseManagementDB];
CREATE USER [<web-app-msi-object-id>] FROM EXTERNAL PROVIDER;
ALTER ROLE db_datareader ADD MEMBER [<web-app-msi-object-id>];
ALTER ROLE db_datawriter ADD MEMBER [<web-app-msi-object-id>];
```

> **Note:**  
> If you get an error about the login not existing, ensure you have created the login in the master database first.

#### c. Assign Enterprise App Permissions (Optional)

If your application requires the Enterprise App (App Registration) to access APIs or resources, assign the necessary roles or API permissions in Azure AD.

---

### 5. Configure Web App Environment Variables

Set the following environment variables for your Web App (in Azure Portal or via CLI):

- `STORAGE_ACCOUNT_URL=https://<storage_account_name>.blob.core.windows.net`
- `SQL_SERVER=<sql-server-name>.database.windows.net`
- `SQL_DATABASE=<database-name>`
- `CLIENT_ID=<output from create-enterprise-app.ps1>`
- `CLIENT_SECRET=<output from create-enterprise-app.ps1>`
- `TENANT_ID=<output from create-enterprise-app.ps1>`
- `SECRET_KEY=<your-random-flask-secret>`

Example using Azure CLI:

```sh
az webapp config appsettings set --name <webAppName> --resource-group <resourceGroupName> --settings KEY=VALUE ...
```

---

## Clean Up

To remove all resources, delete the resource group:

```sh
az group delete --name <resourceGroupName>
```

---

## Notes

- The SQL admin password and other secrets should be stored securely (e.g., Azure Key Vault) in production.
- The deployment scripts assume you are logged in to the correct Azure subscription.
- The Bicep template and scripts are designed for minimal, production-like deployments. Adjust as needed for your environment.

---
