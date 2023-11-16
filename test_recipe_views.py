"""Recipe View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_recipe_views.py


from app import app, CURR_USER_KEY
import os
from unittest import TestCase

from models import db, connect_db, User, Recipe, MealPlan, Day, Ingredient, ShoppingList, ShoppingListIng, RecipeDay, RecipeUser

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

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class RecipeViewTestCase(TestCase):
    """Test views for recipes."""

    def setUp(self):
        """Create test client, add sample data."""
        """Create test client, add sample data."""
        ShoppingListIng.query.delete()
        RecipeDay.query.delete()
        RecipeUser.query.delete()
        ShoppingList.query.delete()
        Ingredient.query.delete()
        Recipe.query.delete()
        Day.query.delete()
        MealPlan.query.delete()
        User.query.delete()

        self.client = app.test_client()

        self.testuser = User.register("test", "email@email.com",
                                      "testFName", "testLName", "password")

        self.testuser_id = 8989
        self.testuser.id = self.testuser_id

        self.u1 = User.register("test1", "email1@email.com",
                                "testFName1", "testLName1", "password")
        self.u1_id = 778
        self.u1.id = self.u1_id

        recipe1 = Recipe(title="TestRecipe",
                         image="TestImage")
        db.session.add(recipe1)
        recid1 = 2222
        recipe1.id = recid1

        self.recipe1 = recipe1
        self.recid1 = recid1

        mp = MealPlan(user_id=self.testuser_id)
        mpid = 2222
        mp.id = mpid

        mp.days.append(Day(name="Sunday", mealplan_id=mp.id))
        mp.days.append(Day(name="Monday", mealplan_id=mp.id))
        mp.days.append(Day(name="Tuesday", mealplan_id=mp.id))
        mp.days.append(Day(name="Wednesday", mealplan_id=mp.id))
        mp.days.append(Day(name="Thursday", mealplan_id=mp.id))
        mp.days.append(Day(name="Friday", mealplan_id=mp.id))
        mp.days.append(Day(name="Saturday", mealplan_id=mp.id))
        shopping_list = ShoppingList(user_id=self.testuser_id)
        db.session.add_all([mp, shopping_list])

        self.mp = mp
        self.mpid = mpid

        db.session.commit()

    def tearDown(self):
        resp = super().tearDown()
        db.session.rollback()
        return resp

    def test_recipe_search(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            resp = c.get('/recipes?q=beef')
            self.assertIn("Beef Wellington", str(resp.data))
            self.assertIn("Beef Carrot Stew", str(resp.data))
            self.assertNotIn("Bed", str(resp.data))
            self.assertNotIn("Table", str(resp.data))

    def test_recipe_show(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            resp = c.get(f'/recipes/{self.recid1}')
            self.assertEqual(resp.status_code, 200)
            self.assertIn("TestRecipe", str(resp.data))
            self.assertIn("TestImage", str(resp.data))

    def test_favorite_recipe(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            resp = c.post(f'/recipes/{self.recid1}/add')
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(len(self.testuser.recipes), 1)

    def test_unfavorite_recipe(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.post(f'/recipes/{self.recid1}/add')
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(len(self.testuser.recipes), 1)

            resp = c.post(f'/recipes/{self.recid1}/remove')
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(len(self.testuser.recipes), 0)

    def test_unauthorized_recipe_page_access(self):
        with self.client as c:
            resp = c.get("/recipes", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertNotIn("Choose your recipes", str(resp.data))
            self.assertIn("Access unauthorized", str(resp.data))
