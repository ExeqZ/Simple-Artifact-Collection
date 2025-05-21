# Simple Artifact Collection

This project is **Simple Artifact Collection**, built with Flask and Azure services. It allows users to upload files to Azure Blob Storage, manage cases with dedicated blob containers, and provides an admin portal for case management. The system uses **Azure SQL Database** for storing case metadata and **Managed Identity** for secure authentication.

---

## Table of Contents
1. [Introduction](#introduction)
2. [Features](#features)
3. [Technologies Used](#technologies-used)
4. [Required Azure Resources](#required-azure-resources)
5. [Automated Deployment](#automated-deployment)
6. [Manual Steps to Prepare the Environment](#manual-steps-to-prepare-the-environment)
7. [Project Structure](#project-structure)
8. [How to Run the Project](#how-to-run-the-project)
9. [Screenshots](#screenshots)
10. [Contributing](#contributing)
11. [License](#license)

---

## Introduction

Simple Artifact Collection is designed to provide a secure and scalable platform for uploading, managing, and organizing files. It leverages Azure services for storage and authentication, ensuring a modern and reliable experience.

---

## Features

- **File Upload Portal**: Users can upload files to specific cases using a secret key.
- **Admin Portal**: Admins can create cases, view case details, and manage files in blob containers.
- **Azure Integration**:
  - **Azure Blob Storage**: Stores uploaded files in dedicated containers.
  - **Azure SQL Database**: Stores case metadata (case name, container name, secret).
  - **Managed Identity**: Securely connects to Azure SQL Database without storing credentials.
- **Dynamic UI**: A responsive and interactive user interface built with modern web technologies.
- **Blob Inventory**: Each container maintains a `.blobinventory` file for fast file hash and metadata lookup.
- **Automated Resource Deployment**: Bicep templates and PowerShell scripts for full Azure resource provisioning.

---

## Technologies Used

- **Flask (Python)**: Backend framework for handling routes and logic.
- **Azure Blob Storage**: Secure storage for uploaded files.
- **Azure SQL Database**: Metadata storage for cases.
- **Microsoft Entra ID (Azure AD)**: Authentication and authorization.
- **Tailwind CSS**: Modern and responsive UI styling.
- **Font Awesome**: Free icons for a polished user interface.
- **Azure Bicep**: Infrastructure as Code for Azure resources.
- **PowerShell**: Deployment automation.

---

## Required Azure Resources

To deploy and run this project, you will need the following Azure resources:
1. **Azure Resource Group**
2. **Azure Storage Account** (StorageV2, general purpose v2)
3. **Azure SQL Database** (Basic, 5 DTU, zone redundant)
4. **Azure Web App** (App Service Plan B1, with Managed Identity)
5. **Microsoft Entra ID (Azure AD) Enterprise Application**

---

## Automated Deployment

All required Azure resources can be deployed using the scripts and templates in the [`resource-deployment`](./resource-deployment) folder.

### Steps:

1. **Edit Parameters**  
   Update `main.parameters.json` in `resource-deployment` with your desired resource names and credentials.

2. **Deploy Azure Resources**  
   Run the deployment script:
   ```powershell
   cd resource-deployment
   ./deploy.ps1
   ```

3. **Create Azure AD Enterprise Application**  
   Run:
   ```powershell
   ./create-enterprise-app.ps1
   ```
   Save the outputted `CLIENT_ID`, `CLIENT_SECRET`, and `TENANT_ID`.

4. **Set Web App Environment Variables**  
   Set the following variables in the Azure Portal or via CLI:
   - `STORAGE_ACCOUNT_URL`
   - `SQL_SERVER`
   - `SQL_DATABASE`
   - `CLIENT_ID`
   - `CLIENT_SECRET`
   - `TENANT_ID`
   - `SECRET_KEY`

   Example:
   ```sh
   az webapp config appsettings set --name <webAppName> --resource-group <resourceGroupName> --settings KEY=VALUE ...
   ```

5. **Assign Permissions**  
   Assign the Web App's managed identity access to the Storage Account and SQL Database as needed.

For more details, see [`resource-deployment/readme.md`](./resource-deployment/readme.md).

---

## Manual Steps to Prepare the Environment

If you want to run the project locally or without automation, follow these steps:

### 1. **Clone the Repository**
```bash
git clone <repository-url>
cd <repository-folder>
```

### 2. **Install Dependencies**
Ensure Python 3.9+ is installed. Install the required Python packages:
```bash
pip install -r requirements.txt
```

### 3. **Set Environment Variables**
Create a `.env` file in the project root with the following variables:
```plaintext
FLASK_APP=app.py
FLASK_ENV=development
STORAGE_ACCOUNT_URL=https://<storage_account_name>.blob.core.windows.net
SQL_SERVER=<sql-server-name>.database.windows.net
SQL_DATABASE=<database-name>
CLIENT_ID=<azure-ad-client-id>
CLIENT_SECRET=<azure-ad-client-secret>
TENANT_ID=<azure-ad-tenant-id>
SECRET_KEY=<your-random-flask-secret>
```

### 4. **Initialize the Database**
Run the following script to create the `Cases` table in Azure SQL Database:
```sql
CREATE TABLE Cases (
    id INT PRIMARY KEY IDENTITY(1,1),
    name NVARCHAR(100) NOT NULL,
    container_name NVARCHAR(100) UNIQUE NOT NULL,
    secret NVARCHAR(50) UNIQUE NOT NULL
);
```

---

## Project Structure

```plaintext
project0010/
│
├── app.py                     # Main Flask application
├── requirements.txt           # Python dependencies
├── templates/                 # HTML templates
│   ├── index.html             # File upload portal
│   ├── admin.html             # Admin portal
│   ├── case.html              # Case details page
│   ├── about.html             # About page
│   └── upload.html            # File upload page
├── static/                    # Static files
│   ├── css/
│   │   └── styles.css         # CSS styles
│   ├── js/
│   │   └── base.js            # JavaScript for menu toggle
│   └── images/
│       └── logo.png           # Application logo
├── resource-deployment/       # Azure Bicep templates and deployment scripts
│   ├── main.bicep
│   ├── main.parameters.json
│   ├── deploy.ps1
│   ├── create-enterprise-app.ps1
│   └── readme.md
└── .env                       # Environment variables (not included in repo)
```

---

## How to Run the Project

### 1. **Run Locally**
Start the Flask development server:
```bash
flask run
```
Access the application at `http://127.0.0.1:5000`.

### 2. **Deploy to Azure**
- Deploy the project to the Azure Web App using Git or Azure CLI:
```bash
az webapp up --name <web-app-name> --resource-group <resource-group-name>
```

---

## Screenshots

### File Upload Portal
![File Upload Portal](https://via.placeholder.com/800x400?text=File+Upload+Portal)

### Admin Portal
![Admin Portal](https://via.placeholder.com/800x400?text=Admin+Portal)

### Case Details
![Case Details](https://via.placeholder.com/800x400?text=Case+Details)

---

## Contributing

Contributions are welcome! Please follow these steps:
1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Submit a pull request with a detailed description of your changes.

---

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.