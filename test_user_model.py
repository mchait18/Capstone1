"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


from app import app
import os
from unittest import TestCase
from sqlalchemy import exc
from models import db, User, MealPlan, Recipe

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


class UserModelTestCase(TestCase):
    """Test views for messages."""

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

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            first_name="fname",
            last_name="lname",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no recipes & no shopping list
        self.assertEqual(len(u.recipes), 0)
        self.assertEqual(len(u.shopping_list), 0)

    def test_user_recipes(self):
        self.u1.recipes.append(self.recipe1)
        db.session.commit()

        self.assertEqual(len(self.u1.recipes), 1)

    def test_valid_signup(self):
        u3 = User.register("test3", "email3@email.com",
                           "testFName2", "testLName2", "testpassword")
        uid3 = 3333
        u3.id = uid3
        db.session.commit()

        u3 = User.query.get(uid3)
        self.assertIsNotNone(u3)
        self.assertEqual(u3.username, "test3")
        self.assertEqual(u3.email, "email3@email.com")
        self.assertEqual(u3.first_name, "testFName2")
        self.assertEqual(u3.last_name, "testLName2")
        self.assertNotEqual(u3.password, "password")
        # Bcrypt strings should start with $2b$
        self.assertTrue(u3.password.startswith("$2b$"))

    def test_invalid_username(self):
        invalid = User.register(None, "email4@email.com", "password",
                                "testFName2", "testLName2")
        uid = 4444
        invalid.id = uid

        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_invalid_email(self):
        invalid = User.register(
            "TestName", None, "testFName2", "testLName2", "password")
        uid = 4444
        invalid.id = uid

        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_invalid_password(self):
        with self.assertRaises(ValueError) as context:
            User.register("TestName", "Test@gmail.com",
                          "testFName2", "testLName2", "")

        with self.assertRaises(ValueError) as context:
            User.register("TestName", "Test@gmail.com",
                          "testFName2", "testLName2", None)

    def test_duplicate_username(self):
        u1 = User.register("Test", "email4@email.com",
                           "password", "testFName2", "testLName2")
        uid = 4444
        u1.id = uid
        db.session.commit()

        invalid = User.register(
            "Test", "emailtest@email.com", "password", "testFName3", "testLName3")
        uid = 123
        invalid.id = uid

        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_valid_authenticate(self):
        test_user = User.authenticate("test1", "password")
        self.assertIsNotNone(test_user)
        self.assertEqual(test_user.id, self.uid1)

    def test_invalid_username(self):
        self.assertFalse(User.authenticate("badusername", "password"))

    def test_wrong_password(self):
        self.assertFalse(User.authenticate("test1", "badpassword"))
