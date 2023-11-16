"""Shopping List model tests."""

# run these tests like:
#
#    python -m unittest test_shoppingList_model.py


from app import app
import os
from unittest import TestCase
from sqlalchemy import exc
from models import db, User, Recipe, Ingredient, ShoppingList

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///mealplanner-test"


# Now we can import app


# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class SLModelTestCase(TestCase):
    """Test views for shopping list."""

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()

        u1 = User.register("test1", "email1@email.com",
                           "testFName", "testLName", "password")
        uid1 = 1111
        u1.id = uid1

        recipe1 = Recipe(title="TestRecipe",
                         image="TestImage")
        db.session.add(recipe1)
        recid1 = 2222
        recipe1.id = recid1

        db.session.commit()

        self.u1 = u1
        self.uid1 = uid1

        self.recipe1 = recipe1
        self.recid1 = recid1

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_shoppinglist_model(self):
        """Does basic model work?"""

        sl = ShoppingList(
            user_id=self.uid1
        )

        db.session.add(sl)
        db.session.commit()

        # user should have 1 shopping list
        self.assertEqual(len(self.u1.shopping_list), 1)
        self.assertEqual(self.u1.shopping_list[0].user_id, self.uid1)

    def test_sl_ingredients(self):
        """testing ingredients functionality"""
        sl = ShoppingList(
            user_id=self.uid1
        )

        db.session.add(sl)
        ing1 = Ingredient(original="ingName",
                          aisle="testAisle",
                          recipe_id=self.recid1)

        ing2 = Ingredient(original="ing2Name",
                          aisle="testAisle",
                          recipe_id=self.recid1)

        db.session.add_all([ing1, ing2])
        sl.ingredients.append(ing1)
        sl.ingredients.append(ing2)
        db.session.commit()

        self.assertEqual(len(sl.ingredients), 2)
        self.assertEqual(
            sl.ingredients[0].original, "ingName")
        self.assertEqual(
            sl.ingredients[1].original, "ing2Name")
