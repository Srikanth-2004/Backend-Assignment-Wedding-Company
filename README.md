# Organization Management Service (Backend Intern Assignment)

This is a backend service built with **FastAPI** and **MongoDB** that supports creating and managing organizations in a multi-tenant architecture. It uses a "Master Database" for metadata and creates dynamic collections for each tenant.

## 🛠️ Tech Stack
* **Framework:** FastAPI (Python)
* **Database:** MongoDB (Async Motor Driver)
* **Authentication:** JWT (JSON Web Tokens) with Bcrypt hashing
* **Validation:** Pydantic models

## 🚀 Key Features
1.  **Multi-Tenancy:**
    * Dynamically creates a new MongoDB collection (`org_<name>`) for every new organization.
    * Maintains a Master Database for global metadata and user credentials.
2.  **Authentication:**
    * Admin login returns a JWT access token.
    * Protected endpoints (Update/Delete) require a valid token.
3.  **CRUD Operations:**
    * Create, Read, Update, and Delete organizations.
    * "Update" includes logic to rename the underlying tenant collection while preserving data.

## Architecture Diagram

<img width="1108" height="650" alt="Backend Architecture" src="https://github.com/user-attachments/assets/489eeffe-c295-45fe-8299-e25bd247220b" />


## ⚙️ Setup Instructions

### Prerequisites
* Python 3.10+
* MongoDB running locally on port 27017

### Installation
1.  **Clone the repository:**
    ```bash
    git clone <your-repo-url>
    cd <repo-name>
    ```

2.  **Create a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Linux/Mac
    # venv\Scripts\activate   # On Windows
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the server:**
    ```bash
    uvicorn app.main:app --reload
    ```

5.  **Access the API:**
    Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) to view the Swagger UI.

## 📝 Usage Guide
1.  **Create an Org:** Use `POST /org/create` to register a new organization and admin.
2.  **Login:** Use `POST /admin/login` with the admin credentials to get an `access_token`.
3.  **Authorize:** Click the "Authorize" button in Swagger UI and paste the token.
4.  **Manage:** You can now use the protected `PUT /org/update` and `DELETE /org/delete` endpoints.
