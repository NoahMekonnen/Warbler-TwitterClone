from unittest import TestCase
from models import db, User, Message, Follows, Likes
import os



os.environ['DATABASE_URL'] = 'postgresql:///warbler-test'

from app import app, CURR_USER_KEY
app.config['TESTING'] = True
app.config['DEBUG'] = True
app.config['WTF_CSRF_ENABLED'] = False

# create the tables

db.create_all()


class UserViewsTestCase(TestCase):

    def setUp(self):

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()
        db.session.commit()
        
        u1 = User.signup(username='test1', email='test1@test.com', password='HASHED_PASSWORD', image_url='')
        u2 = User.signup(username='test2', email='test2@test.com', password='HASHED_PASSWORD', image_url='')
        u3 = User.signup(username='test3', email='test3@test.com', password='HASHED_PASSWORD', image_url='')

        db.session.commit()

        msg1 = Message(text="Blessed Trinity", user_id=u1.id)
        db.session.add(msg1)

        msg2 = Message(text="Mary", user_id=u2.id)
        db.session.add(msg2)
        db.session.commit()

        like1 = Likes(user_id=u1.id, message_id=msg2.id)
        db.session.add(like1)

        follow1 = Follows(user_being_followed_id=u1.id, user_following_id=u2.id)
        db.session.add(follow1)

        follow2 = Follows(user_being_followed_id=u2.id, user_following_id=u1.id)
        db.session.add(follow2)
        db.session.commit()

        self.u1 = u1  
        self.u2 = u2

    def test_list_users(self):
        """Test /users route"""

        with app.test_client() as client:
            resp = client.get('/users')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('@test1', html)

    def test_users_show(self):
        """Test /users/<int:user_id> route"""

        "-Not logged in"
        with app.test_client() as client:
            resp = client.get(f'/users/{self.u1.id}')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<p>Blessed Trinity</p>', html)

        "-Logged in"
        with app.test_client() as client:
            with client.session_transaction() as change_session:
                change_session[CURR_USER_KEY] = self.u1.id

            resp = client.get(f'/users/{self.u1.id}')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<p>Blessed Trinity</p>',html)
        
    def test_show_liked_messages(self):
        """Test users/liked"""

        "-Not logged in"
        with app.test_client() as client:
            resp = client.get("/users/liked", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Access unauthorized.', html)
        
        "-Logged in"
        u1 = User.query.filter_by(username="test1").first()
        with app.test_client() as client:
            with client.session_transaction() as change_session:
                change_session[CURR_USER_KEY] = u1.id
                
            resp = client.get("/users/liked")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Detail', html)
            
    def test_show_following(self):
        user = User.query.filter_by(username="test1").first()

        # Not Logged in
        with app.test_client() as client:
            resp = client.get(f'/users/{self.u1.id}/following', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", html)   

        # Logged in
        with app.test_client() as client:
            with client.session_transaction() as change_session:
                change_session[CURR_USER_KEY] = self.u1.id
                
            resp = client.get(f'/users/{self.u1.id}/following')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('@test2', html)

    def test_users_followers(self):
        # Not logged in
        with app.test_client() as client:
            resp = client.get(f'/users/{self.u1.id}/followers', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Access unauthorized', html)

        # Logged in
        with app.test_client() as client:
            with client.session_transaction() as change_session:
                change_session[CURR_USER_KEY] = self.u1.id

            resp = client.get(f'/users/{self.u1.id}/followers', follow_redirects=True)
            html = resp.get_data(as_text=True)
        
            self.assertEqual(resp.status_code, 200)
            self.assertIn('@test2', html)

    def test_add_follow(self):
        # Not logged in
        with app.test_client() as client:
            resp = client.post(f'/users/follow/{self.u1.id}', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", html)

        #Logged in
        u3 = User.query.filter_by(username='test3').first()
        with app.test_client() as client:
            with client.session_transaction() as change_session:
                change_session[CURR_USER_KEY] = self.u1.id

            resp = client.post(f'/users/follow/{u3.id}', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('@test2', html)
            user = User.query.filter_by(username='test1').first()
            self.assertEqual(len(user.following), 2)

    def test_stop_following(self):

        # Not logged in
        with app.test_client() as client:
            resp = client.post(f'/users/stop-following/{self.u1.id}', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", html)
            
        # Logged in
        u2 = User.query.filter_by(username='test2').first()
        with app.test_client() as client:
            with client.session_transaction() as change_session:
                change_session[CURR_USER_KEY] = self.u1.id

            resp = client.post(f'/users/stop-following/{u2.id}', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertNotIn('@test2', html)
            u1 = User.query.filter_by(username='test1').first()
            self.assertEqual(len(u1.following), 0)

    def test_profile(self):
        # Get/ Not Logged in
        with app.test_client() as client:
            resp = client.get('/users/profile', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", html)

        # Get/ Logged in
        u1 = User.query.filter_by(username="test1").first()
        with app.test_client() as client:
            with client.session_transaction() as change_session:
                change_session[CURR_USER_KEY] = u1.id

            resp = client.get('users/profile')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Edit Profile", html)

        # Post/ Not Logged in
        with app.test_client() as client:
            resp = client.get('/users/profile', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", html)

        # Post/ Logged in
        with app.test_client() as client:
            with client.session_transaction() as change_session:
                change_session[CURR_USER_KEY] = u1.id

            resp = (client.post('/users/profile', 
            data=({'username': 'test4', 'bio': "the tester", "password":"HASHED_PASSWORD",
            "email":"test1@test.com"}), 
            follow_redirects=True))

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Delete Profile", html)
            self.assertIn("@test4", html)
            self.assertIn("the tester", html)

        def test_delete_user(self):
            # Not logged in
            with app.test_client() as client:
                resp = client.post('/users/delete')
                html = resp.get_data(as_text=True)

                self.assertEqual(resp.status_code, 200)
                self.assertIn("Access unauthorized", html)

            # Logged in
            with app.test_client() as client:
                with client.session_transaction() as change_session:
                    change_session[CURR_USER_KEY] = self.u1.id
                
                resp = client.post('/users/delete')
                html = resp.get_data(as_text=True)

                self.assertEqual(resp.status_code, 200)
                self.assertIn("Sign me up", html)

    



    

