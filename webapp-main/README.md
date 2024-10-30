
---
 
# Flask Web Application------
 
This document provides the necessary steps to prepare your environment for, build, and deploy a Flask-based web application locally. This application offers a simple user management system with features such as user registration, updating user details, and a health check endpoint to ensure the application's connectivity to its.
 
## Prerequisites----
 
To get started, you will need:
 
- Python 3.6 or newer

- pip for installing Python packages

- MySQL or MariaDB server installed and running--

- An environment for running Flask applications (e.g., Linux, Windows, macOS)
 
## Initial Setup--
 
### 1. Clone the Repository
 
Clone the source code to your local environment using Git:
 
```bash

git clone [URL to your repository]

cd [repository name]

```
 

 
### 2. Install Python Dependencies
 
Create a virtual environment and activate it:
 
```bash

python3 -m venv venv

source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

```
 
Install the required Python packages:
 
```bash

pip install flask flask_sqlalchemy flask_bcrypt pymysql

```
 
### 3. Database Configuration
 
Ensure your MySQL or MariaDB server is running and create a new database:----
 
```sql

CREATE DATABASE mydb;

```
 
Modify the `SQLALCHEMY_DATABASE_URI` in your application to match your database credentials and name:
 
```python

App.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root1234@localhost/mydb'

```
 
### 4. Set Environment Variables
 
For better security, configure the application's secret key as an environment variable before running the application:
 
```bash

export SECRET_KEY='your_secret_key'

```
 

 
## Build and Deployment
 
### 1. Initialize the Database
 
With the Flask application context active, initialize the database schema:
 
```bash

flask shell

>>> from yourapplication import db

>>> db.create_all()

>>> exit()

```
 

 
### 2. Run the Flask Application
 
Run your Flask application using:
 
```bash

flask run

```
 
Or directly through Python:
 
```bash

python -m flask run

```
 
The application will start running on `http://127.0.0.1:5000/`.
 
## Using the Application
 
- **POST /v1/user**: Register a new user.

- **GET /v1/user/self**: Retrieve the details of the currently authenticated user.

- **PUT /v1/user/self**: Update the details of the currently authenticated user.

- **GET /healthz**: Perform a health check of the application and its connection to the database.
 
## Security and Configuration Notes
 
- Always ensure your `SECRET_KEY` is set to a secure, random value in a production environment.

- Regularly update your Python dependencies to mitigate vulnerabilities.

- Configure your MySQL or MariaDB server with strong access controls and passwords.
 test.
---
 

## Python Integration Testing with Pytest and GitHub Actions

This repository contains a Python integration testing suite using Pytest along with GitHub Actions for continuous integration. The integration tests focus on user registration, authentication, and user profile updating functionality of a Flask application.

### Prerequisites

Before running the integration tests, make sure you have the following prerequisites installed:

- Python 3.12
- MySQL (or a compatible database) running with the specified credentials:
  - Database: testdb
  - User: root
  - Password: root1234

### Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/your-repo.git
   cd your-repo
   ```

2. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows, use "venv\Scripts\activate"
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

### Running Locally

You can run the integration tests locally using Pytest. Ensure your MySQL database is running before executing the tests.

```bash
pytest integration_test.py
```

### GitHub Actions Configuration

This repository is configured with GitHub Actions to run the integration tests automatically on every pull request to the `main` branch. The workflow is defined in the `.github/workflows/python-ci.yml` file.

#### Workflow Configuration (`python-ci.yml`)

```yaml
name: Python Continuous Integration

on:
  pull_request:
    branches:
      - main

jobs:
  python-build:
    runs-on: ubuntu-latest
    env:
      DB_DATABASE: testdb
      DB_USER: root
      DB_PASSWORD: root1234

    steps:
    - uses: actions/checkout@v2

    - name: Set up MySQL
      id: setup_mysql
      run: sudo /etc/init.d/mysql start

    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.12'  # Set to your Python version

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        if [ -f requirements.txt ]; then pip install -r requirements.txt; fi

    - name: Check code
      run: |
        python -m compileall -q .
        pytest integration_test.py
```

### Notes

- Ensure your MySQL server is accessible and running before the workflow starts.
- Update the MySQL credentials in the workflow file (`DB_DATABASE`, `DB_USER`, and `DB_PASSWORD`) to match your setup.
- Customize the workflow to include any additional steps or configurations required for your specific application.

Now, with GitHub Actions configured, your integration tests will automatically run on each pull request, providing continuous integration for your Python application.
