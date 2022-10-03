import datetime
from flask import flash, render_template, request, redirect, session, url_for
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from gather import app, db, mongo
from gather.models import Cuisine, User, Favourite


difficulty_levels = ["Easy", "More effort", "A Challenge"]


def is_admin(username):
    """Checks if user had admin permissions."""
    # Can add more usernames to array.
    return username in ["admin", "mit"]


# def get_user_favourites(username):
#     """Returns logged in user's favourite recipes"""
#     # Finds user's favourites in relational database
#     user_favourite_recipes = list(Favourite.query.filter(
#         Favourite.user_name == username))
#     return user_favourite_recipes


def get_favourite_recipes(username):
    """Returns logged in user's favourite recipes"""
    # Finds user's favourites in relational database
    user_favourite_recipes = list(Favourite.query.filter(
        Favourite.user_name == username))
    favourite_recipes = []
    # Finds recipes in non-relational database
    for item in user_favourite_recipes:
        favourite_recipe = mongo.db.recipes.find_one(
            {"_id": ObjectId(item.recipe_id)})
        favourite_recipes.append(favourite_recipe)
    return favourite_recipes


def format_string_to_list(user_input, has_comma_separator=True):
    """Formats user input into arrays for storing in db
    Used for submit recipe and edit recipe
    """
    if has_comma_separator:
        # for use with comma seperated entries
        # also replaces new lines in case values C+V in
        input_remove_new_lines = user_input.replace("\r\n", ",")
        input_list = input_remove_new_lines.split(",")
    else:
        # for use with new line seperated entries
        input_list = user_input.split("\r\n")
    # remove trailing spaces
    input_list_stripped = [i.lstrip() for i in input_list]
    return input_list_stripped


def remove_all_favourites(recipe_id):
    """Used by recipe delete"""
    find_favourites = list(Favourite.query.filter(
        Favourite.recipe_id == (recipe_id)).all())

    if find_favourites:
        for item in find_favourites:
            favourite = Favourite.query.get_or_404(item.id)
            db.session.delete(favourite)
            db.session.commit()
            print("succseess")
        else:
            print("error")
    else:
        print("no favs found")


@app.route("/")
def index():
    """Renders index page"""
    recipes = mongo.db.recipes.find()
    recently_added_recipes = recipes.sort("timestamp", -1).limit(3)
    quick_recipes = mongo.db.recipes.find().sort("duration").limit(3)
    cuisines = list(Cuisine.query.order_by(Cuisine.cuisine_name).all())
    # If user logged in, also finds user favourites
    if "user" in session:
        favourite_recipes = get_favourite_recipes(session["user"])
        return render_template(
            "index.html", recipes=recipes,
            cuisines=cuisines,
            recently_added_recipes=recently_added_recipes,
            quick_recipes=quick_recipes,
            favourite_recipes=favourite_recipes)
    # If user logged out
    else:
        return render_template(
            "index.html", recipes=recipes,
            cuisines=cuisines,
            recently_added_recipes=recently_added_recipes,
            quick_recipes=quick_recipes)


@app.route("/recipes")
def get_recipes():
    """Renders recipes page"""

    # Checks if user is logged in
    if "user" not in session:
        flash("You need to be logged in to view recipes")
        return redirect(url_for("login"))

    recipes = list(mongo.db.recipes.find())
    cuisines = list(Cuisine.query.order_by(Cuisine.cuisine_name).all())
    favourite_recipes = get_favourite_recipes(session["user"])
    return render_template(
        "recipes.html", recipes=recipes,
        cuisines=cuisines,
        favourite_recipes=favourite_recipes)


@app.route("/search", methods=["GET", "POST"])
def search():
    """Renders search results on find recipes page"""
    query = request.form.get("query")
    recipes = list(mongo.db.recipes.find({"$text": {"$search": query}}))
    cuisines = list(Cuisine.query.order_by(Cuisine.cuisine_name).all())
    favourite_recipes = get_favourite_recipes(session["user"])
    return render_template(
        "recipes.html", recipes=recipes,
        cuisines=cuisines,
        favourite_recipes=favourite_recipes)


@app.route("/register", methods=["GET", "POST"])
def register():
    """Renders register page and allows user to register"""
    if request.method == "POST":
        # checks if username already exists
        existing_user = User.query.filter(
            User.user_name == request.form.get("user_name").lower()).all()

        if existing_user:
            flash(
                "Username already exists. Please try a different username")
            return redirect(url_for("register"))

        user = User(
            user_name=request.form.get("user_name").lower(),
            user_first_name=request.form.get("first_name").lower(),
            user_last_name=request.form.get("last_name").lower(),
            password=generate_password_hash(request.form.get("password"))
        )

        # Add user to databsase
        db.session.add(user)
        db.session.commit()

        # put the new user into 'session' cookie
        session["user"] = request.form.get("user_name").lower()
        flash("Registration Successful!")
        return redirect(url_for("get_recipes"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Renders log in page and allows user to login"""
    if request.method == "POST":
        # check if username exists in db
        existing_user = User.query.filter(
            User.user_name == request.form.get("user_name").lower()).all()

        if existing_user:
            print(request.form.get("user_name"))
            # ensure hashed password matches user input
            if check_password_hash(
                    existing_user[0].password, request.form.get("password")):
                session["user"] = request.form.get("user_name").lower()
                flash("Welcome, {}".format(
                    request.form.get("user_name")))
                return redirect(url_for(
                    "get_recipes"))
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
    """Renders users dashboard aka My Recipes page"""
    if "user" in session:
        user_recipes = list(mongo.db.recipes.find({"author": session["user"]}))
        cuisines = list(Cuisine.query.order_by(Cuisine.cuisine_name).all())
        favourite_recipes = get_favourite_recipes(session["user"])
        return render_template(
            "dashboard.html", user_recipes=user_recipes,
            cuisines=cuisines, favourite_recipes=favourite_recipes)

    return redirect(url_for("login"))


@app.route("/logout")
def logout():
    """remove user from session cookie"""
    flash("You have been logged out")
    session.pop("user")
    return redirect(url_for("login"))


@app.route("/recipe/add", methods=["GET", "POST"])
def submit_recipe():
    """Submits user's recipe to db and renders add recipe page"""
    if "user" not in session:
        flash("You need to be logged in to submit a recipe")
        return redirect(url_for("get_recipes"))

    if request.method == "POST":

        # Turns user data into an array to be stored in db
        # Comma seperated entry
        ingrediant_string = request.form.get("ingrediant_list")
        ingrediant_list = format_string_to_list(ingrediant_string)
        # Comma seperated entry
        tags_string = request.form.get("tags")
        tags_list = format_string_to_list(tags_string)
        # New line seperated entry
        instructions_string = request.form.get("instructions")
        instructions_list = format_string_to_list(
            instructions_string, False)

        recipe = {
            "author": session["user"],
            "recipe_name": request.form.get("recipe_name"),
            "tags": tags_list,
            "cuisine_id": request.form.get("cuisine_id"),
            "ingrediant_list": ingrediant_list,
            "serves": request.form.get("serves"),
            "duration": request.form.get("duration", type=int),
            "difficulty": request.form.get("difficulty"),
            "instructions": instructions_list,
            "image_url": request.form.get("image_url"),
            "url": request.form.get("url"),
            "timestamp": datetime.datetime.utcnow()
        }
        # Adds new recipe to db
        mongo.db.recipes.insert_one(recipe)
        flash("Recipe successfully submitted")
        return redirect(url_for("get_recipes"))

    cuisines = list(Cuisine.query.order_by(Cuisine.cuisine_name).all())
    return render_template(
        "submit_recipe.html", cuisines=cuisines,
        difficulty_levels=difficulty_levels)


@app.route("/recipe/<recipe_id>/edit", methods=["GET", "POST"])
def edit_recipe(recipe_id):
    """Edit's user's recipe and renders edit recipe page"""

    try:
        recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})

        if "user" not in session or session["user"] != recipe["author"]:
            flash("You can only edit your own recipes!")
            return redirect(url_for("get_recipes"))

        if request.method == "POST":

            # Turns user data into an array to be stored in db
            # Comma seperated entry
            ingrediant_string = request.form.get("ingrediant_list")
            ingrediant_list = format_string_to_list(ingrediant_string)
            # Comma seperated entry
            tags_string = request.form.get("tags")
            tags_list = format_string_to_list(tags_string)
            # New line seperated entry
            instructions_string = request.form.get("instructions")
            instructions_list = format_string_to_list(
                instructions_string, False)

            edit = {
                "author": session["user"],
                "recipe_name": request.form.get("recipe_name"),
                "tags": tags_list,
                "cuisine_id": request.form.get("cuisine_id"),
                "ingrediant_list": ingrediant_list,
                "serves": request.form.get("serves"),
                "duration": request.form.get("duration", type=int),
                "difficulty": request.form.get("difficulty"),
                "instructions": instructions_list,
                "image_url": request.form.get("image_url"),
                "url": request.form.get("url"),
                "timestamp": datetime.datetime.utcnow()
            }
            # Adds new recipe to db
            mongo.db.recipes.replace_one({"_id": ObjectId(recipe_id)}, edit)
            flash("Recipe successfully edited")
            return redirect(url_for("dashboard"))
    except Exception:
        return redirect(url_for("get_recipes"))

    cuisines = list(Cuisine.query.order_by(Cuisine.cuisine_name).all())
    return render_template(
        "edit_recipe.html", recipe=recipe, cuisines=cuisines,
        difficulty_levels=difficulty_levels)


@app.route("/recipe/<recipe_id>/view", methods=["GET"])
def view_recipe(recipe_id):
    """renders View Recipe page"""
    try:
        recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
        cuisines = list(Cuisine.query.order_by(Cuisine.cuisine_name).all())
        return render_template(
            "view_recipe.html", recipe=recipe, cuisines=cuisines)
    except Exception:
        return redirect(url_for("get_recipes"))


@app.route("/recipe/<recipe_id>/delete", methods=["GET", "POST"])
def delete_recipe(recipe_id):
    """Deletes user's recipe and renders confirm delete page"""

    try:
        recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})

        if "user" not in session or session["user"] != recipe["author"]:
            flash("You can only delete your own recipes!")
            return redirect(url_for("get_recipes"))

        if request.method == "POST":
            # Deletes user's recipe from db
            mongo.db.recipes.delete_one({"_id": ObjectId(recipe_id)})
            remove_all_favourites(recipe_id)
            flash("Recipe successfully deleted")
            return redirect(url_for("dashboard"))

        return render_template("delete_recipe.html", recipe=recipe)

    except Exception:
        return redirect(url_for("get_recipes"))


@app.route("/cuisines")
def manage_cuisines():
    """Renders manage cuisines page"""
    if "user" not in session or not is_admin(session["user"]):
        flash("You must be admin to manage cuisines!")
        return redirect(url_for("get_recipes"))

    cuisines = list(Cuisine.query.order_by(Cuisine.cuisine_name).all())
    return render_template("cuisines.html", cuisines=cuisines)


@app.route("/cuisine/add", methods=["GET", "POST"])
def add_cuisine():
    """ Adds new cuisine to db and renders add cuisine page """
    if "user" not in session or not is_admin(session["user"]):
        flash("You must be admin to manage cuisines!")
        return redirect(url_for("get_recipes"))

    if request.method == "POST":
        # checks if cuisine already exists
        existing_cuisine = Cuisine.query.filter(
            Cuisine.cuisine_name == request.form.get("cuisine_name")).all()

        if existing_cuisine:
            flash("Cuisine already exists")
            return redirect(url_for("add_cuisine"))

        # Adds new cuisine to db
        cuisine = Cuisine(cuisine_name=request.form.get("cuisine_name"))
        db.session.add(cuisine)
        db.session.commit()
        flash("New cuisine added")
        return redirect(url_for("manage_cuisines"))

    return render_template("add_cuisine.html")


@app.route("/cuisine/<int:cuisine_id>/edit", methods=["GET", "POST"])
def edit_cuisine(cuisine_id):
    """ Edits cuisine in db and renders edit cuisine page """
    if "user" not in session or not is_admin(session["user"]):
        flash("You must be admin to manage cuisines!")
        return redirect(url_for("get_recipes"))

    try:
        cuisine = Cuisine.query.get_or_404(cuisine_id)
        if request.method == "POST":
            # Edits cuisine in db
            cuisine.cuisine_name = request.form.get("cuisine_name")
            db.session.commit()
            return redirect(url_for("manage_cuisines"))
        return render_template("edit_cuisine.html", cuisine=cuisine)
    except Exception:
        flash(
            "There was an issue editing that Cuisine name.")
        return redirect(url_for("get_recipes"))


@app.route("/cuisine/<int:cuisine_id>/delete", methods=["GET", "POST"])
def delete_cuisine(cuisine_id):
    """Deletes cuisine from db and renders confirm delete cuisine page"""

    if "user" not in session or not is_admin(session["user"]):
        flash("You must be admin to manage cuisines!")
        return redirect(url_for("get_recipes"))

    try:
        cuisine = Cuisine.query.get_or_404(cuisine_id)
        if request.method == "POST":
            # deletes cuisine from db
            # db.session.delete(cuisine)
            # db.session.commit()

            # makes array with recipe objects to be deleted
            recipes_to_delete = list(
                mongo.db.recipes.find({"cuisine_id": str(cuisine_id)}))
            print(recipes_to_delete)

            for recipe in recipes_to_delete:
                print(recipe)

            
            # iterating through list, filtering by id. Printing.
            # for recipe in recipes_to_delete:
            #     recipe_id = recipe.get("_id")
            #     print(recipe_id)
            #    favourites_to_delete = list(Favourite.query.get_or_404(
            #        Favourite.recipe_id == recipe_id))
            #    for item in favourites_to_delete:
            #        print(item)
            # to add - delete favourite recipes
            # cascade delete recipes
            # mongo.db.recipes.delete_many({"cuisine_id": str(cuisine_id)})
            # flash("Cuisine and associated recipes successfully deleted")
            flash("Testing New route - Ensure return")
            return redirect(url_for("manage_cuisines"))
        return render_template("delete_cuisine.html", cuisine=cuisine)
    except Exception:
        flash("Exception occured")
        return redirect(url_for("get_recipes"))


@app.route("/recipe/<recipe_id>/favourite", methods=["POST"])
def add_favourite(recipe_id):
    """ adds user favourite to db """

    if request.method == "POST":

        favourite = Favourite(
            user_name=session["user"].lower(),
            recipe_id=recipe_id)

        # adds user favourite to relational db
        db.session.add(favourite)
        db.session.commit()

        flash("New favourite added")
        return redirect(url_for("get_recipes"))


@app.route("/recipe/<recipe_id>/unfavourite")
def remove_favourite(recipe_id):
    """ remove user favourite from db """

    find_favourite = Favourite.query.filter(
        Favourite.recipe_id == (recipe_id), Favourite.user_name == (
            session["user"])).first()

    if find_favourite:
        favourite = Favourite.query.get_or_404(find_favourite.id)
        db.session.delete(favourite)
        db.session.commit()

        flash("Favourite Removed")
        return redirect(url_for("get_recipes"))
    else:
        return redirect(url_for("get_recipes"))


@app.route("/recipes/favourites")
def favourites():
    """renders user favourites page"""
    if "user" in session:
        
        try:
            cuisines = list(Cuisine.query.order_by(Cuisine.cuisine_name).all())
            favourite_recipes = list(get_favourite_recipes(session["user"]))
            return render_template(
                "favourite_recipes.html", favourite_recipes=favourite_recipes,
                cuisines=cuisines)
        except:
            flash("An error occured")
            return redirect(url_for("dashboard"))


    flash("You need to be logged in to view favourite recipes")
    return redirect(url_for("login"))
