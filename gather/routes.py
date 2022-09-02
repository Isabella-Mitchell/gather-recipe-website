from flask import flash, render_template, request, redirect, session, url_for
from bson.objectid import ObjectId
from gather import app, db, mongo
from gather.models import Category, User


@app.route("/")
@app.route("/get_recipes")
def get_recipes():
    recipes = mongo.db.recipes.find()
    return render_template("recipes.html", recipes=recipes)