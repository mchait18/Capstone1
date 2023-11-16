"""Models for meal planner"""

from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import datetime

db = SQLAlchemy()
bcrypt = Bcrypt()


def connect_db(app):
    """Connect to database."""

    db.app = app
    db.init_app(app)


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)
    first_name = db.Column(db.String(25),
                           nullable=False)
    last_name = db.Column(db.String(25),
                          nullable=False)
    username = db.Column(db.Text,
                         nullable=False,
                         unique=True)
    password = db.Column(db.Text,
                         nullable=False)
    email = db.Column(db.Text, nullable=False)

    recipes = db.relationship('Recipe',
                              secondary='recipe_user',
                              backref='user')
    shopping_list = db.relationship('ShoppingList', backref='user')
    mealplan = db.relationship('MealPlan', backref='user')

    @classmethod
    def register(cls, username, email, first_name, last_name, password):
        """Register user w/hashed password & return user."""

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            email=email,
            password=hashed_pwd,
            first_name=first_name,
            last_name=last_name
        )

        db.session.add(user)

        return user

    # start_authenticate

    @classmethod
    def authenticate(cls, username, pwd):
        """Validate that user exists & password is correct.

        Return user if valid; else return False.
        """

        u = User.query.filter_by(username=username).first()

        if u and bcrypt.check_password_hash(u.password, pwd):
            # return user instance
            return u
        else:
            return False
    # end_authenticate


class MealPlan(db.Model):
    __tablename__ = "mealplans"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                        nullable=False)

    days = db.relationship('Day', backref='mealplan')


class Day(db.Model):
    __tablename__ = 'days'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, nullable=False)
    mealplan_id = db.Column(db.Integer, db.ForeignKey('mealplans.id'),
                            nullable=False)

    recipes = db.relationship('Recipe', secondary='recipe_day', backref='day')


class Recipe(db.Model):
    __tablename__ = 'recipes'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    image = db.Column(db.Text, nullable=False)
    servings = db.Column(db.Integer)
    instructions = db.Column(db.Text)
    readyInMinutes = db.Column(db.Integer)

    extendedIngredients = db.relationship('Ingredient', backref='recipe')


class RecipeUser(db.Model):
    __tablename__ = 'recipe_user'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                        primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'),
                          primary_key=True)


class RecipeDay(db.Model):
    __tablename__ = 'recipe_day'

    day_id = db.Column(db.Integer, db.ForeignKey('days.id'),
                       primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'),
                          primary_key=True)


class ShoppingList(db.Model):
    __tablename__ = 'shopping_list'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                        nullable=False)
    ingredients = db.relationship(
        'Ingredient', secondary='shopping_list_ing', backref='shopping_list')


class Ingredient(db.Model):
    __tablename__ = 'ingredients'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    original = db.Column(db.Text, nullable=False)
    name = db.Column(db.Text)
    amount = db.Column(db.Numeric)
    unit = db.Column(db.Text)
    aisle = db.Column(db.Text)
    recipe_id = db.Column(db.Integer, db.ForeignKey(
        'recipes.id'), nullable=False)


class ShoppingListIng(db.Model):
    __tablename__ = 'shopping_list_ing'

    shopping_list_id = db.Column(db.Integer, db.ForeignKey('shopping_list.id'),
                                 primary_key=True)
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredients.id'),
                              primary_key=True)
