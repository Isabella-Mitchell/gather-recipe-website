from flask import flash, render_template, request, redirect, session, url_for
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from gather import app, db, mongo
from gather.models import Cuisine, User, Favourite
import datetime
import re


def is_admin(username):
    return username in ["admin", "mit"]


@app.route("/")
@app.route("/recipes")
def get_recipes():
    recipes = mongo.db.recipes.find()
    cuisines = list(Cuisine.query.order_by(Cuisine.cuisine_name).all())
    return render_template("recipes.html", recipes=recipes, cuisines=cuisines)


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

    
@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():        
    if "user" in session:
        user_recipes = mongo.db.recipes.find({"author": session["user"]})
        cuisines = list(Cuisine.query.order_by(Cuisine.cuisine_name).all())
        return render_template(
            "dashboard.html", user_recipes=user_recipes, 
            cuisines=cuisines)

    return redirect(url_for("login"))


@app.route("/logout")
def logout():
    # remove user from session cookie
    flash("You have been logged out")
    session.pop("user")
    return redirect(url_for("login"))


@app.route("/recipe/add", methods=["GET", "POST"])
def submit_recipe():
    if "user" not in session:
        flash("You need to be logged in to submit a recipe")
        return redirect(url_for("get_recipes"))
    
    if request.method == "POST":

        # refactor to reduce repition
        # takes user data and turns it into an array to be stored in MongoDB
        ingrediant_string = request.form.get("ingrediant_list")
        # in case user C+V's in instructions
        ingrediant_remove_new_lines = ingrediant_string.replace("\r\n", ",")
        ingrediant_list = ingrediant_remove_new_lines.split(",")
        ingrediant_list_stripped = [i.lstrip() for i in ingrediant_list]
        tags_string = request.form.get("tags")
        tags_list = tags_string.split(",")
        tags_list_stripped = [i.lstrip() for i in tags_list]
        instructions_string = request.form.get("instructions")
        instructions_list = instructions_string.split("\r\n")
        instructions_list_stripped = [i.lstrip() for i in instructions_list]

        recipe = {
            "author": session["user"],
            "recipe_name": request.form.get("recipe_name"),
            "tags": tags_list_stripped,
            "cuisine_id": request.form.get("cuisine_id"),
            "ingrediant_list": ingrediant_list_stripped,
            "serves": request.form.get("serves"),
            "duration": request.form.get("duration"),
            "difficulty": request.form.get("difficulty"),
            "instructions": instructions_list_stripped,
            "colour_code": request.form.get("colour_code"),
            "url": request.form.get("url"),
            "timestamp": datetime.datetime.utcnow()
        }
        mongo.db.recipes.insert_one(recipe)
        flash("Recipe successfully submitted")
        return redirect(url_for("get_recipes"))

    cuisines = list(Cuisine.query.order_by(Cuisine.cuisine_name).all())
    return render_template("submit_recipe.html", cuisines=cuisines)


@app.route("/recipe/<recipe_id>/edit", methods=["GET", "POST"])
def edit_recipe(recipe_id):

    recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
    
    if "user" not in session or session["user"] != recipe["author"]:
        flash("You can only edit your own recipes!")
        return redirect(url_for("get_recipes"))
    
    if request.method == "POST":

        # refactor to reduce repition
        # takes user data and turns it into an array to be stored in MongoDB
        ingrediant_string = request.form.get("ingrediant_list")
        # in case user C+V's in instructions
        ingrediant_remove_new_lines = ingrediant_string.replace("\r\n", "")
        ingrediant_list = ingrediant_remove_new_lines.split(",")
        ingrediant_list_stripped = [i.lstrip() for i in ingrediant_list]
        tags_string = request.form.get("tags")
        tags_list = tags_string.split(",")
        tags_list_stripped = [i.lstrip() for i in tags_list]
        instructions_string = request.form.get("instructions")
        instructions_list = instructions_string.split("\r\n")
        instructions_list_stripped = [i.lstrip() for i in instructions_list]

        edit = {
            "author": session["user"],
            "recipe_name": request.form.get("recipe_name"),
            "tags": tags_list_stripped,
            "cuisine_id": request.form.get("cuisine_id"),
            "ingrediant_list": ingrediant_list_stripped,
            "serves": request.form.get("serves"),
            "duration": request.form.get("duration"),
            "difficulty": request.form.get("difficulty"),
            "instructions": instructions_list_stripped,
            "colour_code": request.form.get("colour_code"),
            "url": request.form.get("url"),
            "timestamp": datetime.datetime.utcnow()
        }
        mongo.db.recipes.replace_one({"_id": ObjectId(recipe_id)}, edit)
        flash("Recipe successfully edited")
        return redirect(url_for(
                    "dashboard", user_name=session["user"]))
    
    cuisines = list(Cuisine.query.order_by(Cuisine.cuisine_name).all())
    return render_template(
        "edit_recipe.html", recipe=recipe, cuisines=cuisines)


@app.route("/recipe/<recipe_id>/view", methods=["GET"])
def view_recipe(recipe_id):
    try:
        recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
        cuisines = list(Cuisine.query.order_by(Cuisine.cuisine_name).all())
        return render_template(
            "view_recipe.html", recipe=recipe, cuisines=cuisines)
    except:
        return redirect(url_for("get_recipes"))


@app.route("/recipe/<recipe_id>/delete")
def delete_recipe(recipe_id):

    recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})

    if "user" not in session or session["user"] != recipe["author"]:
        flash("You can only delete your own recipes!")
        return redirect(url_for("get_recipes"))

    mongo.db.recipes.delete_one({"_id": ObjectId(recipe_id)})
    flash("Recipe successfully deleted")
    return redirect(url_for("dashboard", user_name=session["user"]))


@app.route("/cuisines")
def manage_cuisines():
    cuisines = list(Cuisine.query.order_by(Cuisine.cuisine_name).all())
    return render_template("cuisines.html", cuisines=cuisines)


@app.route("/cuisine/add", methods=["GET", "POST"])
def add_cuisine():

    if request.method == "POST":
        # checks if cuisine already exists
        existing_cuisine = Cuisine.query.filter(
            Cuisine.cuisine_name == request.form.get(
                "cuisine_name").lower()).all()

        if existing_cuisine:
            flash("Cuisine already exists")
            return redirect(url_for("add_cuisine"))
    
        cuisine = Cuisine(cuisine_name=request.form.get("cuisine_name"))

        db.session.add(cuisine)
        db.session.commit()
        flash("New cuisine added")
        return redirect(url_for("manage_cuisines"))

    return render_template("add_cuisine.html")


@app.route("/cuisine/<int:cuisine_id>/edit", methods=["GET", "POST"])
def edit_cuisine(cuisine_id):
    if "user" not in session or not is_admin(session["user"]):
         flash("You must be admin to manage cuisines!")
         return redirect(url_for("get_recipes"))
    
    cuisine = Cuisine.query.get_or_404(cuisine_id)
    if request.method == "POST":
        cuisine.cuisine_name = request.form.get("cuisine_name")
        db.session.commit()
        return redirect(url_for("manage_cuisines"))
    return render_template("edit_cuisine.html", cuisine=cuisine)


@app.route("/cuisine/<int:cuisine_id>/delete")
def delete_cuisine(cuisine_id):
    if "user" not in session or not is_admin(session["user"]):
         flash("You must be admin to manage cuisines!")
         return redirect(url_for("get_recipes"))

    cuisine = Cuisine.query.get_or_404(cuisine_id)
    db.session.delete(cuisine)
    db.session.commit()
    # mongo.db.Cuisine.delete_many({"cuisine_id": str(cuisine_id)})
    return redirect(url_for("manage_cuisines"))


@app.route("/recipe/<recipe_id>/favourite", methods=["GET", "POST"])
def add_favourite(recipe_id):

    recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
    
    if request.method == "POST":
	
        favourite = Favourite(
            user_name=session["user"].lower(),
            recipe_id=recipe_id
            )

        db.session.add(favourite)
        db.session.commit()

        flash("New favourite added")
        return redirect(url_for("get_recipes"))

    return render_template("add_favourite.html", recipe=recipe)