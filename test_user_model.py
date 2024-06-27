"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows, Likes
from flask_bcrypt import Bcrypt


# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"
bcrypt = Bcrypt()


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        u1 = User(
            email="test1@test.com",
            username="testuser1",
            password="HASHED_PASSWORD"
        )

        db.session.add(u1)
        db.session.commit()

        self.u1 = u1

        u2 = User(
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD"
        )

        db.session.add(u2)
        db.session.commit()

        self.u2 = u2

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)

    def test___repr__(self):
        """__repr__ works as expected"""

        self.assertEqual(self.u1.__repr__(), f"<User #{self.u1.id}: {self.u1.username}, {self.u1.email}>")
        
    def test_is_following(self):
        """checks if is_following method is worker. Also checks if followers and following properties are working"""
        
        self.assertEqual(self.u1.is_following(self.u2), False)
        self.assertEqual(len(self.u1.following), 0)
        self.assertEqual(len(self.u2.followers), 0)

        follow = Follows(user_being_followed_id=self.u2.id,user_following_id=self.u1.id)
        db.session.add(follow)
        db.session.commit()

        #is_following method should return true
        self.assertEqual(self.u1.is_following(self.u2), True)

        #u1 should be following one person and u2 should have one follower
        self.assertEqual(len(self.u1.following), 1)
        self.assertEqual(len(self.u2.followers), 1)
    
    def test_is_followed_by(self):
        """checks if a user is being followed by another"""

        self.assertEqual(self.u1.is_followed_by(self.u2), False)

        follow = Follows(user_being_followed_id=self.u1.id, user_following_id=self.u2.id)
        db.session.add(follow)
        db.session.commit()

        #u1 should be followed by u2
        self.assertEqual(self.u1.is_followed_by(self.u2), True)

    def test_signup(self):
        """check that signup method makes a user"""

        User.signup('testuser3', 'test3@test.com', 'HASHED_PASSWORD','')
        u3 = User.query.filter_by(username='testuser3').first()

        self.assertEqual(u3.username, 'testuser3')
        self.assertEqual(u3.email, 'test3@test.com')
        self.assertTrue(bcrypt.check_password_hash(u3.password, 'HASHED_PASSWORD'))
        
        #Cannot make a user when email is not unique
        # with self.assertRaises(IntegrityError):
        #     User.signup('testuser4', 'test3@test.com', 'HASHED_PASSWORD','')

        #check that password must be non-empty
        with self.assertRaises(ValueError):
            User.signup('test4', 'test4@test.com', None, None)
        

    def test_authenticate(self):
        """checking if authenticate works as expected"""

        #works when give valid username and password
        test1 = User.signup('testuser5', 'test5@test.com', 'HASHED_PASSWORD','')
        self.assertEqual(isinstance(test1, User), True)

        #doesnt work when given invalid username
        u5_invalid_username= User.authenticate('invalid', "HASHED_PASSWORD")
        self.assertEqual(u5_invalid_username, False)

        #doesnt work when given invalid password
        u5_invalid_password = User.authenticate('testuser5', 'invalid')
        self.assertEqual(u5_invalid_password, False)

    def test_messages(self):
        """checks if the message property works as expected"""
        self.assertEqual(len(self.u1.messages),0)
        message = Message(user_id=self.u1.id, text="blessed virgin mary")
        db.session.add(message)
        db.session.commit()

        #there should be one message now
        self.assertEqual(len(self.u1.messages),1)

    def test_likes(self):
        """checks if the likes property works"""
        message = Message(user_id=self.u1.id, text="blessed virgin mary")
        db.session.add(message)
        db.session.commit()

        self.assertEqual(len(self.u2.likes),0)
        like = Likes(user_id=self.u2.id, message_id=message.id)
        db.session.add(like)
        db.session.commit()

        #u2 should have one liked message now
        self.assertEqual(len(self.u2.likes), 1)