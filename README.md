# Recipe Management System

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Flask](https://img.shields.io/badge/Flask-2.3.2-green)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3.0-purple)
![SQLite](https://img.shields.io/badge/SQLite-3-lightgrey)

The **Recipe Management System** is a web application built with Flask that allows users to manage and share their favorite recipes. Users can add, view, edit, and delete recipes, as well as explore recipes shared by others. The application features a user-friendly interface, responsive design, and secure user authentication.

---

## Features

- **User Authentication**:
  - Register, log in, and log out.
  - Securely manage user sessions.

- **Recipe Management**:
  - Add new recipes with details like name, category, description, ingredients, and instructions.
  - View a list of all recipes.
  - Edit or delete your own recipes.

- **Responsive Design**:
  - Built with Bootstrap for a seamless experience on all devices.

- **Image Upload**:
  - Upload images for recipes to make them visually appealing.

- **Search and Filter**:
  - Explore recipes by category or search for specific dishes.

- **User-Friendly Interface**:
  - Intuitive navigation and clean design for ease of use.

---

## Technologies Used

- **Backend**:
  - Python
  - Flask (Web Framework)
  - SQLite (Database)

- **Frontend**:
  - HTML, CSS, JavaScript
  - Bootstrap (Styling Framework)

- **Other Tools**:
  - Flask-WTF (Form Handling)
  - Flask-Login (User Authentication)
  - Werkzeug (Password Hashing)

---

## Installation and Setup

Follow these steps to set up the Recipe Management System on your local machine.

### Prerequisites

- Python 3.8 or higher
- Pip (Python Package Installer)

### Steps

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/GaganRaj05/Recipe-Management-System.git
   cd Recipe-Management-System
   ```

2. **Create a Virtual Environment**:
   ```bash
   python -m venv venv
   ```

3. **Activate the Virtual Environment**:
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Set Up the Database**:
   Run the following command to initialize the SQLite database:
   ```bash
   python
   >>> from app import db
   >>> db.create_all()
   >>> exit()
   ```

6. **Run the Application**:
   ```bash
   python app.py
   ```

7. **Access the Application**:
   Open your browser and navigate to:
   ```
   http://127.0.0.1:5000/
   ```

---

## Usage

1. **Register or Log In**:
   - Create a new account or log in with existing credentials.

2. **Add a Recipe**:
   - Click on "Add your recipe" and fill in the details (name, category, description, ingredients, instructions, and image).

3. **View Recipes**:
   - Browse all recipes on the "Recipes" page.

4. **Edit or Delete Recipes**:
   - Only the recipe owner can edit or delete their recipes.

5. **Log Out**:
   - Securely log out when done.



## Contributing

Contributions are welcome! If you'd like to contribute to this project, please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Commit your changes.
4. Push your branch and submit a pull request.

---

## License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- **Flask Documentation**: For providing excellent resources on building web applications.
- **Bootstrap**: For making it easy to create responsive and modern designs.
- **GaganRaj05**: For creating and maintaining this project.

---

## Contact

For any questions or feedback, feel free to reach out:

- **Gagan Raj**
- Email: [Your Email](gaganraj.dev05@gmail.com)
- GitHub: [GaganRaj05](https://github.com/GaganRaj05)

---

Enjoy managing your recipes with the **Recipe Management System**! 🍲
```

