from flask import Flask, render_template, redirect, url_for, request, flash, session
import mysql.connector  
import os, bcrypt
from dotenv import load_dotenv
from werkzeug.utils import secure_filename

load_dotenv()

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

mysql_config = {
    'host': os.getenv('MYSQL_HOST'),
    'user': os.getenv('MYSQL_USER'),
    'password': os.getenv('MYSQL_PASSWORD'),
    'database': os.getenv('MYSQL_DB')
}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def get_db_connection():
    """Helper function to create a MySQL connection."""
    return mysql.connector.connect(**mysql_config)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def handle_recipe_results(db_results):
    recipe_list = []
    for row in db_results:
        recipe_dict = {
            "recipe_id": row[0],
            "title": row[1],
            "description": row[2],
            "image_path": row[3]
        }
        recipe_list.append(recipe_dict)
    return recipe_list

@app.route('/', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["Email"]
        password = request.form["Password"].encode('utf-8')
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)  
        cursor.execute("SELECT user_id, email, password FROM Users WHERE email = %s", (email,))
        result = cursor.fetchone()
        if result:
            user_id, db_email, db_password = result['user_id'], result['email'], result['password']
            print(result)
            if bcrypt.checkpw(password, db_password):
                session["user_id"] = user_id
                session["email"] = email
                session["password"] = password
                flash("Login success", "success")
                return redirect(url_for('home'))
            else:
                flash("Incorrect password", "danger")
                return redirect(url_for('login'))
        else:
            flash("No users found.. register to use this app", "danger")
            return redirect(url_for('login'))
        cursor.close()
        conn.close()
    else:
        return render_template('login.html')

@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        user_name = request.form["user_name"]
        email = request.form["Email"]
        password = request.form["password"].encode('utf-8')
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT username, email FROM Users WHERE username = %s OR email = %s", (user_name, email))
        result = cursor.fetchone()
        if result:
            flash("User exists, please enter new username or email", "danger")
            return redirect(url_for('register'))
        hashed_pw = bcrypt.hashpw(password, bcrypt.gensalt())
        try:
            cursor.execute("INSERT INTO Users (username, email, password) VALUES (%s, %s, %s)", (user_name, email, hashed_pw))
            conn.commit()
            flash("Registration successful", "success")
            return redirect(url_for('login'))
        except Exception as e:
            flash(f"Registration failed: {e}", "danger")
            conn.rollback()
        finally:
            cursor.close()
            conn.close()
    return render_template("register.html")

@app.route('/home')
def home():
    return render_template("home.html")

@app.route('/AddRecipe', methods=["GET", "POST"])
def add_recipe():
    if request.method == "POST":
        file = request.files['image']
        if file.filename == '':
            return "No selected file"
        if allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.static_folder, 'uploads', filename))
            file_save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename).replace('\\', '/')
            category = request.form["category"]
            title = request.form["title"]
            description = request.form["description"]
            instructions = request.form["instructions"]
            ingredients = request.form['ingredients']

            try:
                conn = get_db_connection()
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SELECT category_id FROM Category WHERE category_name = %s", (category,))
                result = cursor.fetchone()
                if result:
                    category_id = result['category_id']
                    user_id = session.get("user_id")
                    cursor.execute("INSERT INTO Recipes (user_id, title, description, ingredients, instructions, category_id, image_path) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                                  (user_id, title, description, ingredients, instructions, category_id, file_save_path))
                    conn.commit()
                    flash("Recipe uploaded successfully", "success")
                    return redirect(url_for("add_recipe"))
                else:
                    flash("Category required", "danger")
                    return redirect(url_for('add_recipe'))
            except Exception as e:
                flash(f"Some error occurred: {e}", "danger")
                return redirect(url_for('add_recipe'))
            finally:
                cursor.close()
                conn.close()
        else:
            flash("Allowed images are -> png, jpg, jpeg, gif", "danger")
            return render_template("addARecipe.html")
    return render_template("addARecipe.html")

@app.route('/recipes')
def Recipes():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT Recipe_id, title, description, image_path FROM Recipes")
        temp = cursor.fetchall()
        if not temp:
            raise Exception("No data found")
        recipes_list = handle_recipe_results(temp)
        return render_template("Recipes.html", recipes=recipes_list)
    except Exception as e:
        flash(f"No recipes found: {e}", "danger")
        return render_template("Recipes.html")
    finally:
        cursor.close()
        conn.close()

@app.route('/read-full-recipe/<int:recipe_id>')
def complete_recipe(recipe_id):
    if not recipe_id:
        flash("Some error occurred, please try again later", "danger")
        return render_template("CompleteRecipe.html")
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT image_path, description, ingredients, instructions FROM Recipes WHERE Recipe_id = %s", (recipe_id,))
        db_recipe_data = cursor.fetchone()
        if not db_recipe_data:
            raise Exception("Some error occurred, please try again later")
        recipe_data = {
            "recipe_id": recipe_id,
            "image_path": db_recipe_data['image_path'],
            "description": db_recipe_data['description'],
            "ingredients": db_recipe_data['ingredients'],
            "instruction": db_recipe_data['instructions']
        }
        return render_template("CompleteRecipe.html", recipes=[recipe_data])
    except Exception as e:
        flash(f"{e}", "danger")
        return render_template("CompleteRecipe.html")
    finally:
        cursor.close()
        conn.close()

@app.route('/your-recipes')
def your_recipes():
    user_id = session.get("user_id")
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT Recipe_id, title, description, ingredients, instructions, image_path FROM Recipes WHERE user_id = %s", (user_id,))
        db_recipes = cursor.fetchall()
        if not db_recipes:
            flash("No recipes found", "warning")
        recipe_list = []
        for i in db_recipes:
            recipe_dict = {
                "recipe_id": i[0],
                "title": i[1],
                "description": i[2],
                "ingredients": i[3],
                "instructions": i[4],
                "image_path": i[5]
            }
            recipe_list.append(recipe_dict)
        return render_template("your_recipes.html", recipes=recipe_list)
    except Exception as e:
        flash(f"Some error occurred while fetching recipes: {e}", "danger")
        return render_template("your_recipes.html")
    finally:
        cursor.close()
        conn.close()

@app.route('/delete-recipe/<int:recipe_id>')
def delete_recipe(recipe_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Recipes WHERE recipe_id = %s", (recipe_id,))
        conn.commit()
        flash("Recipe deleted successfully", "success")
        return redirect(url_for('your_recipes'))
    except Exception as e:
        flash(f"Some error occurred while deleting your recipes: {e}", "danger")
        return redirect(url_for('your_recipes'))
    finally:
        cursor.close()
        conn.close()

@app.route('/edit-recipes/<int:recipe_id>', methods=["GET", "POST"])
def edit_recipe(recipe_id):
    if request.method == "GET":
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT title, description, ingredients, instructions FROM Recipes WHERE Recipe_id = %s", (recipe_id,))
            db_result = cursor.fetchone()
            recipe_dict = {
                "title": db_result['title'],
                "description": db_result['description'],
                "ingredients": db_result['ingredients'],
                "instructions": db_result['instructions']
            }
            return render_template("editRecipe.html", recipe=recipe_dict)
        except Exception as e:
            flash(f"Some error occurred: {e}", "danger")
            return redirect(url_for('your_recipes'))
        finally:
            cursor.close()
            conn.close()
    elif request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]
        ingredients = request.form["ingredients"]
        instructions = request.form["instructions"]
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE Recipes SET title = %s, description = %s, ingredients = %s, instructions = %s WHERE Recipe_id = %s",
                          (title, description, ingredients, instructions, recipe_id))
            conn.commit()
            flash("Recipe updated successfully", "success")
            return redirect(url_for('your_recipes'))
        except Exception as e:
            flash(f"Some error occurred editing your recipes: {e}", "danger")
            return redirect(url_for('your_recipes'))
        finally:
            cursor.close()
            conn.close()

@app.route('/logout')
def logout():
    session.pop("user_id")
    session.pop("email")
    session.pop("password")
    flash("Logout successful", "success")
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=False)