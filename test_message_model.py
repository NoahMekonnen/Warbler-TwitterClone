"""Message model tests."""

# run these tests like:
#
#    python -m unittest test_message_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class MessageModelTestCase(TestCase):
    """Test views for messages."""
    def setUp(self):

        User.query.delete()
        Message.query.delete()

        u1 = User(
            email="test1@test.com",
            username="testuser1",
            password="HASHED_PASSWORD"
        )

        db.session.add(u1)
        db.session.commit()
        self.u1 = u1

        m1 = Message(
            text="blessed virgin mary",
            user_id=self.u1.id
        )
    
        db.session.add(m1)
        db.session.commit()

        self.m1 = m1
    
    def test_message_model(self):
        """checks if the basic model works"""

        m = Message(
            text="Blessed Trinity",
            user_id=self.u1.id
        )

        db.session.add(m)
        db.session.commit()

        #m should have u1's user_id
        self.assertEqual(m.user_id, self.u1.id)

    def test_user(self):
        """checks the user property works"""

        self.assertEqual(self.m1.user, self.u1)