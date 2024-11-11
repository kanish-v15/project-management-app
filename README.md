# Project Management App

A simple yet effective Project Management Application developed using Django, Python, and MySQL. This app is designed to help users manage tasks, projects, and deadlines efficiently with user authentication and role-based access.

## Features

- **User Authentication**: Register, login, and logout features with secure password management.
- **Project and Task Management**: Create, update, and delete projects and tasks.
- **Role-Based Access**: Different user roles (Project Manager, Team Lead, Employee) with specific permissions.
- **Dashboard**: Summary of all active projects, tasks, and deadlines.

## Tech Stack

- **Backend**: Django (Python)
- **Database**: MySQL
- **Frontend**: HTML, CSS, JavaScript
- **Other**: Django ORM for database interactions, Django's built-in authentication

## Installation

1. **Clone the repository**:
    ```bash
    git clone https://github.com/kanish-v15/project-management-app.git
    ```
2. **Navigate to the project directory**:
    ```bash
    cd project-management-app
    ```
3. **Create and activate a virtual environment**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```
4. **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
5. **Set up the database**:
   - Make sure MySQL is running.
   - Create a MySQL database for the project.
   - Update the `DATABASES` section in `settings.py` with your database credentials.

6. **Apply migrations**:
    ```bash
    python manage.py migrate
    ```
7. **Create a superuser**:
    ```bash
    python manage.py createsuperuser
    ```
8. **Run the server**:
    ```bash
    python manage.py runserver
    ```

## Usage

- Visit `http://127.0.0.1:8000` in your browser.
- Log in with your credentials or register a new account.
- Create and manage projects and tasks as per your role and permissions.

## Folder Structure

- **/project_management**: Main Django application folder with core files.
- **/templates**: HTML files for the frontend.
- **/static**: CSS, JS, and image files.
- **requirements.txt**: Python dependencies.

## Contributing

1. Fork the repository.
2. Create your feature branch (`git checkout -b feature/AmazingFeature`).
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4. Push to the branch (`git push origin feature/AmazingFeature`).
5. Open a pull request.

## License

This project is licensed under the MIT License.
