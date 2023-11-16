"""Recipe View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_sl_views.py


from app import app, CURR_USER_KEY
import os
from unittest import TestCase

from models import db, connect_db, User, Recipe, MealPlan, Day, Ingredient, ShoppingList, ShoppingListIng, RecipeDay, RecipeUser

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

# os.environ['DATABASE_URL'] = "postgresql:///mealplanner-test"


# Now we can import app


# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class SLViewTestCase(TestCase):
    """Test views for recipes."""

    def setUp(self):
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

        self.shopping_list = shopping_list

        ing1 = Ingredient(original="Test1", recipe_id=self.recid1)
        ing2 = Ingredient(original="Test2", recipe_id=self.recid1)
        db.session.add_all([mp, shopping_list, ing1, ing2])

        self.ing1 = ing1
        self.ing2 = ing2

        db.session.commit()

    def tearDown(self):
        resp = super().tearDown()
        db.session.rollback()
        return resp

    def test_sl_show(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            resp = c.get('/shopping_list')
            # self.assertEqual(resp.status_code, 200)
            # self.assertIn("Shopping List", str(resp.data))

    def test_unauthorized_shoppinglist_page_access(self):
        with self.client as c:
            resp = c.get("/shopping_list", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertNotIn("Shopping List", str(resp.data))
            self.assertIn("Access unauthorized", str(resp.data))
