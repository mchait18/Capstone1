"""Meal pLan model tests."""

# run these tests like:
#
#    python -m unittest test_mealplan_model.py


from app import app
import os
from unittest import TestCase
from sqlalchemy import exc
from models import db, User, Recipe, Ingredient, MealPlan, Day

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


class MPModelTestCase(TestCase):
    """Test views for meal plan."""

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()

        u1 = User.register("test1", "email1@email.com",
                           "testFName", "testLName", "password")
        uid1 = 1111
        u1.id = uid1

        db.session.commit()

        self.u1 = u1
        self.uid1 = uid1

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_mealplan_model(self):
        """Does basic model work?"""

        mp = MealPlan(user_id=self.uid1)
        db.session.add(mp)

        db.session.commit()

        # user should have 1 meal plan
        self.assertIsNotNone(self.u1.mealplan)
        self.assertEqual(len(self.u1.mealplan), 1)
        self.assertEqual(self.u1.mealplan[0].user_id, self.uid1)

    def test_mp_days(self):
        """testing days functionality"""
        mp = MealPlan(user_id=self.uid1)
        mpid = 2222
        mp.id = mpid

        mp.days.append(Day(name="Sunday", mealplan_id=mp.id))
        mp.days.append(Day(name="Monday", mealplan_id=mp.id))
        mp.days.append(Day(name="Tuesday", mealplan_id=mp.id))
        mp.days.append(Day(name="Wednesday", mealplan_id=mp.id))
        mp.days.append(Day(name="Thursday", mealplan_id=mp.id))
        mp.days.append(Day(name="Friday", mealplan_id=mp.id))
        mp.days.append(Day(name="Saturday", mealplan_id=mp.id))

        db.session.add(mp)
        db.session.commit()

        self.assertEqual(len(mp.days), 7)
        self.assertEqual(
            mp.days[0].name, "Sunday")
        self.assertEqual(
            mp.days[2].name, "Tuesday")
        self.assertEqual(
            mp.days[0].mealplan_id, mpid)
        self.assertEqual(
            mp.days[2].mealplan_id, mpid)
