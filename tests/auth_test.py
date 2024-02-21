import unittest
from frontend.website import create_app, db

class AuthTest(unittest.TestCase):
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
    
    def test_load_register_form(self):
        response = self.client.get('/register', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Register', response.data)
        self.assertIn(b'First Name', response.data)
        self.assertIn(b'Password', response.data)
        self.assertIn(b'Confirm Password', response.data)
        self.assertIn(b'Submit', response.data)
    
    def test_register_user_valid(self):
        response = self.client.post('/register', data={
            "name": "Test",
            "email": "test@gmail.com",
            "password": "StrongPassword123!",
            "confirm_password": "StrongPassword123!"
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Welcome!", response.data)
        
            

if __name__ == '__main__':
    unittest.main()