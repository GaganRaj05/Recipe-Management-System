from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_mysqldb import MySQL
import os, bcrypt
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB')
mysql = MySQL(app)

@app.route('/', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["Email"]
        password = request.form["Password"].encode('utf-8')
        cursor = mysql.connection.cursor()
        cursor.execute("select email, password from Users where email=%s ", (email,))
        result = cursor.fetchone()
        if result:
            db_email, db_password = result
            if bcrypt.checkpw(password, db_password):
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
            flash("Username taken", "danger")
            return redirect(url_for('register'))
        hashed_pw = bcrypt.hashpw(password, bcrypt.gensalt())
        try:
            cursor.execute("insert into Users (username, email, password) values (%s, %s, %s)", (user_name, email, hashed_pw))
            mysql.connection.commit()
            flash("Registration successful", "success")
            return redirect(url_for('login'))
        except Exception as e:
            flash(f"Registration failed: {e}", "danger")
            mysql.connection.rollback()
        finally:
            cursor.close()
    return render_template("register.html")

@app.route('/home')
def home():
    return render_template("home.html")

if __name__ == "__main__":
    app.run(debug=True)