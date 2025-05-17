# File Upload and Management System

This project is a **File Upload and Management System** built with Flask and Azure services. It allows users to upload files to Azure Blob Storage, manage cases with dedicated blob containers, and provides an admin portal for case management. The system uses **Azure SQL Database** for storing case metadata and **Managed Identity** for secure authentication.

---

## Table of Contents
1. [Introduction](#introduction)
2. [Features](#features)
3. [Technologies Used](#technologies-used)
4. [List of Required Resources](#list-of-required-resources)
5. [Manual Steps to Prepare the Environment](#manual-steps-to-prepare-the-environment)
6. [Project Structure](#project-structure)
7. [How to Run the Project](#how-to-run-the-project)
8. [Screenshots](#screenshots)
9. [Contributing](#contributing)
10. [License](#license)

---

## Introduction

The File Upload and Management System is designed to provide a secure and scalable platform for uploading, managing, and organizing files. It leverages Azure services for storage and authentication, ensuring a modern and reliable experience.

---

## Features

- **File Upload Portal**: Users can upload files to specific cases using a secret key.
- **Admin Portal**: Admins can create cases, view case details, and manage files in blob containers.
- **Azure Integration**:
  - **Azure Blob Storage**: Stores uploaded files in dedicated containers.
  - **Azure SQL Database**: Stores case metadata (case name, container name, secret).
  - **Managed Identity**: Securely connects to Azure SQL Database without storing credentials.
- **Dynamic UI**: A responsive and interactive user interface built with modern web technologies.

---

## Technologies Used

- **Flask (Python)**: Backend framework for handling routes and logic.
- **Azure Blob Storage**: Secure storage for uploaded files.
- **Azure SQL Database**: Metadata storage for cases.
- **Microsoft Entra ID (Azure AD)**: Authentication and authorization.
- **Tailwind CSS**: Modern and responsive UI styling.
- **Font Awesome**: Free icons for a polished user interface.

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
- Configure the **Redirect URI** (e.g., `https://<web-app-name>.azurewebsites.net/auth/callback`).
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