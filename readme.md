# File Upload and Management System

This project is a **File Upload and Management System** built with Flask, Vue.js, and Azure services. It allows users to upload files to Azure Blob Storage, manage cases with dedicated blob containers, and provides an admin portal for case management. The system uses **Azure SQL Database** for storing case metadata and **Managed Identity** for secure authentication.

---

## Table of Contents
1. [Introduction](#introduction)
2. [Features](#features)
3. [List of Required Resources](#list-of-required-resources)
4. [Manual Steps to Prepare the Environment](#manual-steps-to-prepare-the-environment)
5. [Project Structure](#project-structure)
6. [How to Run the Project](#how-to-run-the-project)
7. [Screenshots](#screenshots)
8. [Contributing](#contributing)
9. [License](#license)

---

## Introduction

This project is designed to provide a secure and scalable file upload and management system using Azure services. It includes:
- A **user portal** for uploading files to specific cases.
- An **admin portal** for managing cases and viewing files in blob containers.
- Integration with **Azure SQL Database** for case metadata storage.
- Authentication using **Microsoft Entra ID (Azure AD)**.
- Secure file uploads using **Azure Blob Storage**.

---

## Features

- **File Upload Portal**: Users can upload files to specific cases using a secret key.
- **Admin Portal**: Admins can create cases, view case details, and manage files in blob containers.
- **Azure Integration**:
  - **Azure Blob Storage**: Stores uploaded files in dedicated containers.
  - **Azure SQL Database**: Stores case metadata (case name, container name, secret).
  - **Managed Identity**: Securely connects to Azure SQL Database without storing credentials.
- **Dynamic UI**: Built with Vue.js for a responsive and interactive user experience.

---

## List of Required Resources

To deploy and run this project, you will need the following Azure resources:
1. **Azure Web App**: To host the Flask application.
2. **Azure Blob Storage**: To store uploaded files.
3. **Azure SQL Database**: To store case metadata.
4. **Microsoft Entra ID (Azure AD)**: For user authentication.
5. **Azure Managed Identity**: For secure authentication to Azure SQL Database.

---

## Manual Steps to Prepare the Environment

### 1. **Set Up Azure Resources**
#### a. **Azure Blob Storage**
- Create a **Storage Account** in Azure.
- Note the **Storage Account URL** (e.g., `https://<storage_account_name>.blob.core.windows.net`).

#### b. **Azure SQL Database**
- Create an **Azure SQL Database**.
- Configure a **SQL Server** and database (e.g., `CaseManagementDB`).
- Enable **Azure Active Directory Authentication**.
- Assign the **Managed Identity** of your Azure Web App the appropriate **Microsoft Entra ID role** to contribute to the database:
  - Navigate to your **Azure SQL Server** in the Azure Portal.
  - Under the **Access control (IAM)** section, click **Add role assignment**.
  - Assign the **SQL DB Contributor** role to the **Managed Identity** of your Azure Web App.

#### c. **Microsoft Entra ID (Azure AD)**
- Register an **Azure AD Application**.
- Configure the **Redirect URI** (e.g., `https://<web-app-name>.azurewebsites.net/getAToken`).
- Note the **Client ID**, **Client Secret**, and **Tenant ID**.

#### d. **Azure Web App**
- Create an **Azure Web App**.
- Enable **System-assigned Managed Identity**.

---

### 2. **Prepare the Local Environment**
#### a. **Clone the Repository**
```bash
git clone <repository-url>
cd <repository-folder>
```

#### b. **Install Dependencies**
Ensure Python 3.9+ is installed. Install the required Python packages:
```bash
pip install -r requirements.txt
```

#### c. **Set Environment Variables**
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
```

#### d. **Initialize the Database**
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
│   ├── manage.html            # File management portal
│   ├── admin.html             # Admin portal
│   └── case.html              # Case details page
├── static/                    # Static files
│   ├── css/
│   │   └── styles.css         # CSS styles
│   ├── js/
│   │   ├── index.js           # JavaScript for file upload portal
│   │   ├── manage.js          # JavaScript for file management portal
│   │   ├── admin.js           # JavaScript for admin portal
│   │   └── case.js            # JavaScript for case details page
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