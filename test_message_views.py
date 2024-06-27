"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False

db.create_all()

class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        db.session.commit()

        u1 = User.signup(username='test1', email='test1@test.com', password='HASHED_PASSWORD', image_url='')
        u2 = User.signup(username='test2', email='test2@test.com', password='HASHED_PASSWORD', image_url='')
    
        db.session.commit()

        msg1 = Message(text="Blessed Trinity", user_id=u1.id)
        msg2 = Message(text="Trust in God", user_id=u2.id)
        db.session.add(msg1)
        db.session.add(msg2)
        db.session.commit()

        self.u1 = u1
        self.msg1 = msg1
        self.msg2 = msg2


    def test_messages_add(self):
        """Can add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:
        "A user who is logged in can make a new message"
        with app.test_client() as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.post("/messages/new", data={"text": "Hello"})
            html = resp.get_data(as_text=True)

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.filter_by(text="Hello").first()
            self.assertEqual(msg.text, "Hello")

            "You can also delete a message if you're logged in"
            resp2 = c.post(f"/messages/{msg.id}/delete")
            html2 = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 302)
            self.assertFalse(msg.id in [message.id for message in Message.query.all()])

        "Someone who is not logged in cannot make a new message"
        with app.test_client() as c:
            resp = c.post('/messages/new', data={"text": 'Hello2' }, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertNotIn('Hello2', html)
            self.assertIn('Access unauthorized', html)

        "Get / and Not logged in"
        with app.test_client() as c:
            resp = c.get('/messages/new', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", html)

        "Get / and logged in"
        with app.test_client() as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1.id

            resp = c.get('/messages/new')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Add my message", html)

    def test_messages_show(self):
        # Not logged in
        with app.test_client() as c:
            resp = c.get(f'/messages/{self.msg1.id}')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertNotIn("Delete", html)
            self.assertIn("Blessed Trinity", html)

        # Logged in
        with app.test_client() as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1.id

            resp = c.get(f'/messages/{self.msg1.id}')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Delete", html)
            self.assertIn("Blessed Trinity", html)

    def test_messages_destroy(self):
        # Not logged in
        with app.test_client() as c:
            resp = c.post(f'/messages/{self.msg1.id}/delete', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", html)

        # Logged in
        u1 = User.query.filter_by(username='test1').first()
        with app.test_client() as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = u1.id

            # msg1 = Message.query.filter_by(text="Blessed Trinity")
            resp = c.post(f'/messages/{self.msg1.id}/delete', follow_redirects=True)
            html = resp.get_data(as_text=True)
            messages = Message.query.all()

            self.assertEqual(resp.status_code, 200)
            self.assertEqual(len(Message.query.all()), 1)
            self.assertIn("@test1", html)
            self.assertIn("Messages", html)
            self.assertIn("Likes", html)

        # Deleting message for another user while logged in
        msg2 = Message.query.filter_by(text="Trust in God").first()
        with app.test_client() as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = u1.id

            resp = c.post(f'/messages/{msg2.id}/delete', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertEqual(len(Message.query.all()), 0)
           

