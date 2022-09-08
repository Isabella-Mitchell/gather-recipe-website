from flask import flash, render_template, request, redirect, session, url_for
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from gather import app, db, mongo
from gather.models import Category, Cuisine, User
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
    if "user" not in session:
        flash("You need to be logged in to submit a recipe")
        return redirect(url_for("get_recipes"))
    
    if request.method == "POST":
        recipe = {
            "author": session["user"],
            "recipe_name": request.form.get("recipe_name"),
            "tags": request.form.getlist("tags"),
            "ingrediant_list": request.form.getlist("ingrediant_list"),
            "equipment_list": request.form.getlist("equipment_list"),
            "serves": request.form.get("serves"),
            #"cuisine": request.form.get("cuisine"),
            "cuisine_id": request.form.get("cuisine_id"),
            "duration": request.form.get("duration"),
            "difficulty": request.form.get("difficulty"),
            "instructions": request.form.get("instructions"),
            "url": request.form.get("url"),
            "timestamp": datetime.datetime.utcnow()
        }
        mongo.db.recipes.insert_one(recipe)
        flash("Recipe successfully submitted")
        return redirect(url_for("get_recipes"))

    cuisines = list(Cuisine.query.order_by(Cuisine.cuisine_name).all())
    return render_template("submit_recipe.html")


@app.route("/edit_recipe/<recipe_id>", methods=["GET", "POST"])
def edit_recipe(recipe_id):

    recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
    
    if "user" not in session or session["user"] != recipe["author"]:
        flash("You can only edit your own recipes!")
        return redirect(url_for("get_recipes"))
    
    if request.method == "POST":
        edit = {
            "author": session["user"],
            "recipe_name": request.form.get("recipe_name"),
            "tags": request.form.getlist("tags"),
            "ingrediant_list": request.form.getlist("ingrediant_list"),
            "equipment_list": request.form.getlist("equipment_list"),
            "serves": request.form.get("serves"),
            #"cuisine": request.form.get("cuisine"),
            "cuisine_id": request.form.get("cuisine_id"),
            "duration": request.form.get("duration"),
            "difficulty": request.form.get("difficulty"),
            "instructions": request.form.get("instructions"),
            "url": request.form.get("url"),
            "timestamp": datetime.datetime.utcnow()
        }
        mongo.db.recipes.replace_one({"_id": ObjectId(recipe_id)}, edit)
        flash("Recipe successfully edited")

    cuisines = list(Cuisine.query.order_by(Cuisine.cuisine_name).all())
    return render_template("edit_recipe.html", recipe=recipe)


@app.route("/delete_recipe/<recipe_id>")
def delete_recipe(recipe_id):

    recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})

    if "user" not in session or session["user"] != recipe["author"]:
        flash("You can only delete your own recipes!")
        return redirect(url_for("get_recipes"))

    mongo.db.recipes.delete_one({"_id": ObjectId(recipe_id)})
    flash("Recipe successfully deleted")
    return redirect(url_for("dashboard", user_name=session["user"]))


@app.route("/manage_cuisines")
def manage_cuisines():

    cuisines = list(Cuisine.query.order_by(Cuisine.cuisine_name).all())
    return render_template("cuisines.html", cuisines=cuisines)


@app.route("/add_cuisine", methods=["GET", "POST"])
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


@app.route("/edit_cuisine/<int:cuisine_id>", methods=["GET", "POST"])
def edit_cuisine(cuisine_id):
    # if "user" not in session or session["user"] != "admin":
    #     flash("You must be admin to manage cuisines!")
    #     return redirect(url_for("get_recipes"))
    
    cuisine = Cuisine.query.get_or_404(cuisine_id)
    if request.method == "POST":
        cuisine.cuisine_name = request.form.get("cuisine_name")
        db.session.commit()
        return redirect(url_for("manage_cuisines"))
    return render_template("edit_cuisine.html", cuisine=cuisine)


@app.route("/delete_cuisine/<int:cuisine_id>")
def delete_cuisine(cuisine_id):
    # if session["user"] != "admin":
    #     flash("You must be admin to manage cuisine!")
    #     return redirect(url_for("get_recipes"))

    cuisine = Cuisine.query.get_or_404(cuisine_id)
    db.session.delete(cuisine)
    db.session.commit()
    # mongo.db.Cuisine.delete_many({"cuisine_id": str(cuisine_id)})
    return redirect(url_for("manage_cuisines"))