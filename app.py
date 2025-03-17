from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_mysqldb import MySQL
import os, bcrypt
from dotenv import load_dotenv
from werkzeug.utils import secure_filename


load_dotenv()

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {"png","jpg","jpeg","gif"}

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
mysql = MySQL(app)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS

def handle_recipe_results(db_results):
    recipe_list = []
    for row in db_results:
        recipe_dict = {
            "recipe_id":row[0],
            "title":row[1],
            "description":row[2],
            "image_path":row[3]
        }
        recipe_list.append(recipe_dict)
        
    return recipe_list


@app.route('/', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["Email"]
        password = request.form["Password"].encode('utf-8')
        cursor = mysql.connection.cursor()
        cursor.execute("select user_id,email, password from Users where email=%s ", (email,))
        result = cursor.fetchone()
        if result:
            user_id, db_email, db_password = result
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
    else:
        return render_template('login.html')

@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        user_name = request.form["user_name"]
        email = request.form["Email"]
        password = request.form["password"].encode('utf-8')
        cursor = mysql.connection.cursor()
        cursor.execute("select username,email from Users where username=%s and email=%s", (user_name,email))
        result = cursor.fetchone()
        if result:
            print(result)
            flash("Username taken", "danger")
            return redirect(url_for('register'))
        hashed_pw = bcrypt.hashpw(password, bcrypt.gensalt())
        try:
            cursor.execute("insert into Users (username, email, password) values (%s, %s, %s)", (user_name, email, hashed_pw))
            mysql.connection.commit()
            flash("Registration successful", "success")
            return redirect(url_for('login'))
        except Exception as e:
            flash(f"Registration failed: ", "danger")
            mysql.connection.rollback()
        finally:
            cursor.close()
    return render_template("register.html")

@app.route('/home')
def home():
    return render_template("home.html")

@app.route('/AddRecipe',methods=["GET","POST"])
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
                cursor = mysql.connection.cursor()
                cursor.execute("select category_id from Category where category_name=%s",(category,))
                result = cursor.fetchone()
                if result:
                    category_id = result[0]
                    user_id = session.get("user_id")
                    cursor.execute("insert into Recipes (user_id, title, description, ingredients, instructions, category_id, image_path) values(%s,%s,%s,%s,%s,%s,%s)",(user_id,title,description,ingredients,instructions,category_id,file_save_path))
                    mysql.connection.commit()
                    flash("Recipe uploaded successfully","success")
                    return redirect(url_for("add_recipe"))
                else:
                    flash("category required")
                    return redirect(url_for('add_recipe'))
            except Exception as e:
                flash("Some error occured try again later", "danger")
                return redirect(url_for('add_recipe')) 
        else:
           flash("allowed images are ->png,jpg,jpeg,gif")
           return render_template("addARecipe.html")
    return render_template("addARecipe.html")
    
@app.route('/recipes')
def Recipes():
    try :
        print("working")
        cursor = mysql.connection.cursor()
        cursor.execute("select Recipe_id, title, description,image_path from Recipes")
        temp = cursor.fetchall()
        if not temp:
            raise Exception("No data found")
        recipes_list = handle_recipe_results(temp)
        print(recipes_list)
        return render_template("Recipes.html",recipes = recipes_list)

    except Exception as e:
        print(f"exception :{e}")
        flash("No recipes found","danger")
        return render_template("Recipes.html")

@app.route('/read-full-recipe/<int:recipe_id>')
def complete_recipe(recipe_id):
    if not recipe_id:
        flash(f"Some error occured please try again later","danger")
        return render_template("CompleteRecipe.html")
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("select image_path, description, ingredients,instructions from Recipes where Recipe_id = %s",(recipe_id,))
        db_recipe_data = cursor.fetchone()
        if not db_recipe_data:
            raise Exception("Some error occured please try again later")
        recipe_data = []
        print(db_recipe_data)
        recipe_dict = {
            "recipe_id":recipe_id,
            "image_path":db_recipe_data[0],
            "description":db_recipe_data[1],
            "ingredients":db_recipe_data[2],
            "instruction":db_recipe_data[3]
        }
        recipe_data.append(recipe_dict)
        return render_template("CompleteRecipe.html",recipes = recipe_data)
    except Exception as e:
        flash(f"{e}","danger")
        render_template("CompleteRecipe.html")
    return render_template("CompleteRecipe.html")

@app.route('/your-recipes')
def your_recipes():
    user_id = session.get("user_id")
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("select Recipe_id, title, description, ingredients,instructions,image_path from Recipes where user_id=%s",(user_id,))
        db_recipes = cursor.fetchall()
        if(not db_recipes):
            flash(f"No recipes found","warning")
        recipe_list = []
        for i in db_recipes:
            recipe_dict = {
                "recipe_id":i[0],
                "title":i[1],
                "description":i[2],
                "ingredients":i[3],
                "instructions":i[4],
                "image_path":i[5]
            }
            recipe_list.append(recipe_dict)
            
        return render_template("your_recipes.html",recipes = recipe_list)
        
    except Exception as e:
        print(f"{e}")
        flash(f"some error occured while fetching recipes","danger")
    return render_template("your_recipes.html")

@app.route('/delete-recipe/<int:recipe_id>')
def delete_recipe(recipe_id):
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("delete from Recipes where recipe_id=%s",(recipe_id,))
        mysql.connection.commit()
        flash(f"Recipe deleted successfully","success")
        return redirect(url_for('your_recipes'))
    except Exception as e:
        print(f"{e}")
        flash(f"Some error occured while deleting your recipes")
        return redirect(url_for('your_recipes'))
    
@app.route('/edit-recipes/<int:recipe_id>',methods=["GET","POST"])
def edit_recipe(recipe_id):
    if request.method == "GET":
        cursor = mysql.connection.cursor()
        cursor.execute("select title,description,ingredients,instructions from Recipes where Recipe_id=%s ",(recipe_id,))
        db_result = cursor.fetchone()
        recipe_dict = {
            "title":db_result[0],
            "description":db_result[1],
            "ingredients":db_result[2],
            "instructions":db_result[3]
        }
        return render_template("editRecipe.html",recipe=recipe_dict)
    elif request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]
        ingredients = request.form["ingredients"]
        instructions = request.form["instructions"]
        try:
            cursor = mysql.connection.cursor()
            cursor.execute("update Recipes set title=%s,description=%s,ingredients=%s,instructions=%s where Recipe_id=%s",(title,description,ingredients,instructions,recipe_id))
            mysql.connection.commit()
            flash(f"Recipe updated successfully","success")
            return redirect(url_for('your_recipes'))
        except Exception as e:
            print(f"{e}")
            flash(f"Some error occured editing your recipes","danger")
            return redirect(url_for('your_recipes'))
            
if __name__ == "__main__":
    app.run(debug=True)