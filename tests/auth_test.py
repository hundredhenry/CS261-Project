import unittest
from frontend.website import create_app, db
from frontend.website.models import User

class AuthBase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.db = db
        self.db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def register_user(self, firstname="Test",
                      email="test@gmail.com",
                      password="StrongPassword123!",
                      confirm_password="StrongPassword123!"):
        return self.client.post('/register', data={
            "name": firstname,
            "email": email,
            "password": password,
            "confirm_password": confirm_password
        }, follow_redirects=True)
class RegistrationTest(AuthBase):
        
    def test_load_register_form(self):
        response = self.client.get('/register', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        test_strings = [b'Register', b'First Name', b'Password', b'Confirm Password', b'Submit']

        for test_string in test_strings:
            self.assertIn(test_string, response.data)
    
    def test_register_user_valid_data(self):
        response = self.register_user()
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Welcome!", response.data)
    
    def test_register_user_invalid_firstname(self):
        test_names = ["", "123", "Test123", "Test!@#", "John Doe", "John_Doe"]
        for firstname in test_names:
            response = self.register_user(
                firstname=firstname
            )
            self.assertEqual(response.status_code, 200)
            self.assertNotIn(b"Welcome!", response.data)        
    
    def test_register_use_extreme_firstname(self):
        test_names = ["a", "a"*15]
        for firstname in test_names:
            try:
                response = self.register_user(
                    firstname=firstname
                )
                self.assertEqual(response.status_code, 200)
                self.assertIn(b"Welcome!", response.data, "Failed for firstname: " + firstname)        
            finally:
                user = User.query.filter_by(firstname=firstname).first()
                if user:
                    db.session.delete(user)
                    db.session.commit()
    
    def test_register_user_invalid_email(self):
        test_emails = ["", "test", "test@", "test@gmail", "test@gmail.", "@gmail.com",
                       "test@gmail..com", "test@gmail.c", "test@gmail.com ", "test@gmail.com.",
                       "test@gmail.com/test", "test@gmail.com,test"]
        for email in test_emails:
            response = self.register_user(
                email=email
            )
            self.assertEqual(response.status_code, 200)
            self.assertNotIn(b"Welcome!", response.data)

    def test_register_user_invalid_password(self):
        test_passwords = ["", "123", "abc", "123abcd", "pass", "!@#", "pwd", "short"]
        for password in test_passwords:
            response = self.register_user(
                password=password
            )
            self.assertEqual(response.status_code, 200)
            self.assertNotIn(b"Welcome!", response.data)

    def test_register_user_non_matching_password(self):
        response = self.register_user(
            password="StrongPassword123!",
            confirm_password="StrongPassword123"
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(b"Welcome!", response.data)
    
    def test_register_user_existing_email(self):
        response = self.register_user()
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Welcome!", response.data)
        response = self.register_user()
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(b"Welcome!", response.data)

class LoginTest(AuthBase):
    def setUp(self):
        super().setUp()
        self.register_user()
        user = User.query.filter_by(email="test@gmail.com").first()
        if user:
            user.verified = True
            db.session.commit()
        
    def login_user(self, email="test@gmail.com", password="StrongPassword123!"):
        return self.client.post('/login', data={
            "email": email,
            "password": password
        }, follow_redirects=True)
        
    def test_load_login_form(self):
        response = self.client.get('/login', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        test_strings = [b'Login', b'Email', b'Password', b'Submit']

        for test_string in test_strings:
            self.assertIn(test_string, response.data)
    
    def test_login_user_unverified_email(self):
        user = User.query.filter_by(email="test@gmail.com").first()
        if user:
            user.verified = False
            db.session.commit()
        
        response = self.login_user()
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(b"Welcome", response.data)
        
    def test_login_user_valid_data(self):
        response = self.login_user()
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Welcome", response.data)
        self.assertIn(b"Logout", response.data)
    
    def test_login_user_invalid_email(self):
        test_emails = ["", "test", "test@", "test@gmail", "test@gmail.", "@gmail.com",
                       "test@gmail..com", "test@gmail.c"]
        for email in test_emails:
            response = self.login_user(
                email=email
            )
            self.assertEqual(response.status_code, 200)
            self.assertNotIn(b"Welcome", response.data)
            self.assertNotIn(b"Logout", response.data)
    
    def test_login_user_invalid_password(self):
        test_passwords = ["","strongpassword123!", "123", "abc", "123abcd", "pass", "!@#", "pwd", "short"]
        for password in test_passwords:
            response = self.login_user(
                password=password
            )
            self.assertEqual(response.status_code, 200)
            self.assertNotIn(b"Welcome", response.data)
            self.assertNotIn(b"Logout", response.data)
    
if __name__ == '__main__':
    unittest.main()