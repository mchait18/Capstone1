"""Flask app for Meal Planner"""
from flask_debugtoolbar import DebugToolbarExtension
from fractions import Fraction
import collections
import numpy as np
import pandas as pd
import requests
from sqlalchemy.exc import IntegrityError
from forms import UserAddForm, LoginForm
from models import db, connect_db, User, Recipe, MealPlan, Day, Ingredient, ShoppingList
from flask import Flask, render_template, request, flash, redirect, session, g
import os
from dotenv import load_dotenv
load_dotenv()
# from app_secrets import API_SECRET_KEY
API_SECRET_KEY = os.environ.get('API_SECRET_KEY')

CURR_USER_KEY = "curr_user"
API_BASE_URL = "https://api.spoonacular.com"

app = Flask(__name__)
if "FLASK_ENV" in os.environ:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///mealplanner-test'
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///mealplanner'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = "oh-so-secret"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.app_context().push()
debug = DebugToolbarExtension(app)

connect_db(app)

##############################################################################
# User signup/login/logout


@app.before_request
def add_user_to_g():
    """IF we're logged in, add curr user to Flask global"""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


def do_login(user):
    """Log in user"""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout User"""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


@app.route('/signup', methods=["GET", "POST"])
def signup():
    """handle user signup
     Create new user and add to DB. Redirect to home page.

    If form not valid, present form.

    If the there already is a user with that username: flash message
    and re-present form.
    """
    form = UserAddForm()

    if form.validate_on_submit():

        try:
            user = User.register(
                username=form.username.data,
                email=form.email.data,
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                password=form.password.data)
            db.session.commit()

        except IntegrityError:
            flash("Username already taken", "danger")
            return render_template('users/signup.html', form=form)

        """Initialize a meal plan for user after signup"""
        mealplan = MealPlan(user_id=user.id)
        mealplan.days.append(Day(name="Sunday", mealplan_id=mealplan.id))
        mealplan.days.append(Day(name="Monday", mealplan_id=mealplan.id))
        mealplan.days.append(Day(name="Tuesday", mealplan_id=mealplan.id))
        mealplan.days.append(Day(name="Wednesday", mealplan_id=mealplan.id))
        mealplan.days.append(Day(name="Thursday", mealplan_id=mealplan.id))
        mealplan.days.append(Day(name="Friday", mealplan_id=mealplan.id))
        mealplan.days.append(Day(name="Saturday", mealplan_id=mealplan.id))
        shopping_list = ShoppingList(user_id=user.id)
        db.session.add_all([mealplan, shopping_list])

        db.session.commit()

        do_login(user)
        return redirect('/')

    else:
        return render_template('users/signup.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login"""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.first_name} {user.last_name}!", "success")
            return redirect("/")

        flash('Invalid credentials.', "danger")

    return render_template('users/login.html', form=form)


@app.route('/logout')
def logout():
    """Handle logout of user"""

    do_logout()
    flash("Goodbye", "info")
    return redirect('/')

##############################################################################
# General recipe routes:


@app.route("/")
def homepage():
    """Render homepage."""
    if g.user:
        return render_template('home.html')

    else:
        return render_template('home-anon.html')


@app.route("/recipes")
def recipe_search():
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    search_term = request.args.get("q")
    session['SEARCH_TERM'] = search_term
    res = requests.get(f"{API_BASE_URL}/recipes/complexSearch",
                       params={'query': search_term, "apiKey": API_SECRET_KEY,
                               "number": 12})

    data = res.json()
    return render_template('home.html', recipes=data["results"])


@app.route('/recipes/<int:recipe_id>')
def show_recipe(recipe_id):
    """show recipe"""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    """first check if we have the recipe saved, and if not, grab it from the API"""
    recipe = Recipe.query.get(recipe_id)

    if not recipe:
        res = requests.get(f"{API_BASE_URL}/recipes/{recipe_id}/information",
                           params={"apiKey": API_SECRET_KEY})
        recipe = res.json()

    favorites = [recipe.id for recipe in g.user.recipes]

    return render_template('recipes/detail.html', recipe=recipe, favorites=favorites)


@app.route('/recipes/<int:recipe_id>/add', methods=["GET", "POST"])
def add_recipe(recipe_id):
    """Add recipe to recipe box"""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    """first check if we have the recipe saved, and if not, grab it from the API"""
    recipe = Recipe.query.get(recipe_id)

    if not recipe:
        """retrieve recipe info from API"""
        res = requests.get(f"{API_BASE_URL}/recipes/{recipe_id}/information",
                           params={"apiKey": API_SECRET_KEY})

        data = res.json()

        instructions = data["instructions"] or None
        """create recipe in DB"""
        recipe = Recipe(id=data["id"],
                        title=data["title"],
                        image=data["image"],
                        servings=data["servings"],
                        instructions=instructions,
                        readyInMinutes=data["readyInMinutes"])
        db.session.add(recipe)
        db.session.commit()

        for ingredient in data["extendedIngredients"]:
            ing = Ingredient(original=ingredient["original"],
                             name=ingredient["name"],
                             amount=ingredient["measures"]["us"]["amount"],
                             unit=ingredient["measures"]["us"]["unitShort"],
                             aisle=ingredient["aisle"],
                             recipe_id=recipe.id)

            db.session.add(ing)
            db.session.commit()

            recipe.extendedIngredients.append(ing)

    g.user.recipes.append(recipe)

    db.session.commit()
    favorites = [recipe.id for recipe in g.user.recipes]

    return render_template('recipes/detail.html', recipe=recipe, favorites=favorites)


@app.route('/recipes/<int:recipe_id>/remove', methods=["GET", "POST"])
def remove_recipe(recipe_id):
    """Remove recipe from recipe box"""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    g.user.recipes = [r for r in g.user.recipes if not r.id == recipe_id]

    db.session.commit()
    favorites = [recipe.id for recipe in g.user.recipes]

    return render_template('recipes/liked.html', recipes=g.user.recipes)


@app.route('/recipes/liked')
def show_favorite_recipe():
    """show favorite recipes"""

    return render_template('recipes/liked.html', recipes=g.user.recipes)


##############################################################################
# General mealplanner routes:


@app.route('/mealplanner')
def mealplanner():
    """show meal plan """
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    mealplan = MealPlan.query.filter(MealPlan.user_id == g.user.id).one()

    return render_template('/mealplanner/detail.html', mpDays=mealplan.days)


@app.route('/mealplanner/<int:recipe_id>/add', methods=["GET", "POST"])
def mealplanner_add(recipe_id):
    """add recipe to meal plan"""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    """fist check DB for recipe"""
    recipe = Recipe.query.get(recipe_id)
    """if not in DB, get recipe from API and add it to DB"""
    if not recipe:
        res = requests.get(f"{API_BASE_URL}/recipes/{recipe_id}/information",
                           params={"apiKey": API_SECRET_KEY})
        data = res.json()

        instructions = data["instructions"] or None
        """create recipe in DB"""
        recipe = Recipe(id=data["id"],
                        title=data["title"],
                        image=data["image"],
                        servings=data["servings"],
                        instructions=instructions,
                        readyInMinutes=data["readyInMinutes"])
        db.session.add(recipe)
        db.session.commit()

        for ingredient in data["extendedIngredients"]:
            ing = Ingredient(original=ingredient["original"],
                             name=ingredient["name"],
                             amount=ingredient["measures"]["us"]["amount"],
                             unit=ingredient["measures"]["us"]["unitShort"],
                             aisle=ingredient["aisle"],
                             recipe_id=recipe.id)
            db.session.add(ing)
            db.session.commit()

            recipe.extendedIngredients.append(ing)

    """We need to add ingredients to the shopping list"""
    """First get user's shopping list"""
    shopping_list = ShoppingList.query.filter_by(user_id=g.user.id).one()

    for ingredient in recipe.extendedIngredients:
        shopping_list.ingredients.append(ingredient)

    db.session.commit()
    """get selected day and add recipe to that day in mealplan"""
    selected_day = request.form["day"]

    mealplan = MealPlan.query.filter_by(user_id=g.user.id)

    day_of_mealplan = Day.query.filter(
        Day.name == selected_day, Day.mealplan_id == mealplan[0].id).one()

    try:
        day_of_mealplan.recipes.append(recipe)
        db.session.commit()
    except IntegrityError:
        flash("Recipe already chosen for that day", "danger")
        return redirect('/mealplanner')

    return redirect('/mealplanner')


@app.route('/mealplanner/<int:recipe_id>/remove', methods=["GET", "POST"])
def mealplanner_remove(recipe_id):
    """remove recipe from meal plan"""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    recipe = Recipe.query.get(recipe_id)

    """We need to remove ingredients from the shopping list"""
    """First get user's shopping list"""
    shopping_list = ShoppingList.query.filter_by(user_id=g.user.id).one()

    shopping_list.ingredients = [
        ing for ing in shopping_list.ingredients if ing not in recipe.extendedIngredients]

    db.session.commit()
    """get selected day and remove recipe from that day in mealplan"""
    selected_day = request.form["day-name"]

    mealplan = MealPlan.query.filter_by(user_id=g.user.id)
    day_of_mealplan = Day.query.filter(
        Day.name == selected_day, Day.mealplan_id == mealplan[0].id).one()
    day_of_mealplan.recipes = [
        r for r in day_of_mealplan.recipes if not r == recipe]
    db.session.commit()

    return redirect('/mealplanner')

##############################################################################
# General shopping list routes:


@app.route('/shopping_list')
def get_shopping_list():
    """show shopping list"""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    shopping_list = ShoppingList.query.filter_by(user_id=g.user.id).one()
    ingDicts = [{ing.name: f'{Fraction(ing.amount)} {ing.unit}'}
                for ing in shopping_list.ingredients]
    df = pd.DataFrame([list(attr.items())[0] for attr in ingDicts],
                      columns=['key', 'value'])
    compiled_df = df.drop_duplicates(
        subset='key', keep=False).to_dict(orient="list")
    duplicated_df = df[df.key.duplicated(keep=False)].to_dict(orient="list")
    data = {}
    for key, val in zip(duplicated_df['key'], duplicated_df['value']):
        data[key] = str(data.get(key, 0)) + " + " + str(val)

    ingredients = [f'{val} {key}' for val, key in zip(
        compiled_df['value'], compiled_df['key'])]

    dup_ings = [f'{val[4:]} {key}' for key, val in data.items()]

    return render_template('shopping_list/detail.html', ingredients=ingredients, dup_ingredients=dup_ings)

# @app.route('/shopping_list', methods=["POST"])
# def update_shopping_list():
#     """Update shopping list"""
#     if not g.user:
#         flash("Access unauthorized.", "danger")
#         return redirect("/")

#     shopping_list = ShoppingList.query.filter_by(user_id=g.user.id).one()
#     checked_ingredients = request.form.getlist("ingredients")
#     checked_ingredients = [int(id) for id in checked_ingredients]
#     shopping_list.ingredients = [
#         i for i in shopping_list.ingredients if i.id not in checked_ingredients]

#     return render_template('shopping_list/detail.html', shopping_list=shopping_list.ingredients)


##############################################################################
# Turn off all caching in Flask
#   (useful for dev; in production, this kind of stuff is typically
#   handled elsewhere)
#
# https://stackoverflow.com/questions/34066804/disabling-caching-in-flask


@app.after_request
def add_header(req):
    """Add non-caching headers on every request."""

    req.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    req.headers["Pragma"] = "no-cache"
    req.headers["Expires"] = "0"
    req.headers['Cache-Control'] = 'public, max-age=0'
    return req
