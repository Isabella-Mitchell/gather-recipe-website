from flask import flash, render_template, request, redirect, session, url_for
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from gather import app, db, mongo
from gather.models import Category, User
import datetime


@app.route("/")
@app.route("/get_recipes")
def get_recipes():
    recipes = mongo.db.recipes.find()
    return render_template("recipes.html", recipes=recipes)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # checks if username already exists
        existing_user = User.query.filter(
            User.user_name == request.form.get("user_name").lower()).all()

        if existing_user:
            flash("Username already exists")
            return redirect(url_for("register"))
        
        user = User(
            user_name=request.form.get("user_name").lower(),
            user_first_name=request.form.get("first_name").lower(),
            user_last_name=request.form.get("last_name").lower(),
            password=generate_password_hash(request.form.get("password"))
        )
        
        db.session.add(user)
        db.session.commit()

        # put the new user into 'session' cookie
        session["user"] = request.form.get("user_name").lower()
        flash("Registration Successful!")
        return redirect(url_for("get_recipes"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # check if username exists in db
        existing_user = User.query.filter(User.user_name == 
            request.form.get("user_name").lower()).all()

        if existing_user:
            print(request.form.get("user_name"))
            # ensure hashed password matches user input
            if check_password_hash(
                    existing_user[0].password, request.form.get("password")):
                session["user"] = request.form.get("user_name").lower()
                flash("Welcome, {}".format(
                    request.form.get("user_name")))
                return redirect(url_for(
                    "dashboard", user_name=session["user"]))
            else:
                # invalid password match
                flash("Incorrect Username and/or Password")
                return redirect(url_for("login"))

        else:
            # username doesn't exist
            flash("Incorrect Username and/or Password")
            return redirect(url_for("login"))

    return render_template("login.html")

    
@app.route("/dashboard/<user_name>", methods=["GET", "POST"])
def dashboard(user_name):
        
    if "user" in session:
        user_recipes = mongo.db.recipes.find({"author": session["user"]})
        return render_template(
            "dashboard.html", user_name=session["user"], user_recipes=user_recipes)

    return redirect(url_for("login"))


@app.route("/logout")
def logout():
    # remove user from session cookie
    flash("You have been logged out")
    session.pop("user")
    return redirect(url_for("login"))


@app.route("/submit_recipe", methods=["GET", "POST"])
def submit_recipe():
    if request.method == "POST":
        recipe = {
            "author": session["user"],
            "recipe_name": request.form.get("recipe_name"),
            "tags": request.form.getlist("tags"),
            "ingrediant_list": request.form.getlist("ingrediant_list"),
            "equipment_list": request.form.getlist("equipment_list"),
            "serves": request.form.get("serves"),
            "cuisine": request.form.get("cuisine"),
            "duration": request.form.get("duration"),
            "difficulty": request.form.get("difficulty"),
            "instructions": request.form.get("instructions"),
            "url": request.form.get("url"),
            "timestamp": datetime.datetime.utcnow()
        }
        mongo.db.recipes.insert_one(recipe)
        flash("Recipe successfully submitted")
        return redirect(url_for("get_recipes"))

    return render_template("submit_recipe.html")


@app.route("/edit_recipe/<recipe_id>", methods=["GET", "POST"])
def edit_recipe(recipe_id):
    if request.method == "POST":
        edit = {
            "author": session["user"],
            "recipe_name": request.form.get("recipe_name"),
            "tags": request.form.getlist("tags"),
            "ingrediant_list": request.form.getlist("ingrediant_list"),
            "equipment_list": request.form.getlist("equipment_list"),
            "serves": request.form.get("serves"),
            "cuisine": request.form.get("cuisine"),
            "duration": request.form.get("duration"),
            "difficulty": request.form.get("difficulty"),
            "instructions": request.form.get("instructions"),
            "url": request.form.get("url"),
            "timestamp": datetime.datetime.utcnow()
        }
        mongo.db.recipes.replace_one({"_id": ObjectId(recipe_id)}, edit)
        flash("Recipe successfully edited")

    recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
    return render_template("edit_recipe.html", recipe=recipe)