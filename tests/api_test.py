from auth_test import AuthBase
from sentify.website.models import User, Notification

class APITests(AuthBase):
    def setUp(self):
        super().setUp()
        self.register_user()
        self.user = User.query.filter_by(email="test@gmail.com").first()
        if self.user:
            self.user.verified = True
            self.db.session.commit()
            self.login_user()

    def test_modify_follow_incorrect_method(self):
        response = self.client.get('/api/modify/follow', follow_redirects=True)
        self.assertEqual(response.status_code, 405)
        self.assertIn(b"Method Not Allowed", response.data)
    
    def test_modify_follow_no_args(self):
        response = self.client.post('/api/modify/follow',
                                    headers = {"Content-Type": "application/json"},
                                    json={}, follow_redirects=False)
        self.assertEqual(response.status_code, 400)
        self.assertEqual({'error': 'No ticker provided'}, response.json)
    
    def test_modify_follow_no_ticker(self):
        response = self.client.post('/api/modify/follow',
                                    headers = {"Content-Type": "application/json"},
                                    json={'ticker': ''}, follow_redirects=False)
        self.assertEqual(response.status_code, 400)
        self.assertEqual({'error': 'No ticker provided'}, response.json)
    
    def test_modify_follow_invalid_ticker(self):
        for ticker in ["Apple", "a", "LONGSTRING", "123", "!£TI"]:
            response = self.client.post('/api/modify/follow',
                                        headers = {"Content-Type": "application/json"},
                                        json={'ticker': ticker}, follow_redirects=False)
            self.assertEqual(response.status_code, 404)
            self.assertEqual({'error': 'Ticker does not exist'}, response.json)

    def test_modify_follow_valid_ticker(self):
        for ticker in ["AAPL", "GOOG", "MSFT", "KO"]:
            response = self.client.post('/api/modify/follow',
                                        headers = {"Content-Type": "application/json"},
                                        json={'ticker': ticker}, follow_redirects=False)
            self.assertEqual(response.status_code, 200)
            self.assertEqual({'status': 'followed', 'ticker': ticker}, response.json)
        
    def test_modify_unfollow_valid_ticker(self):
        self.test_modify_follow_valid_ticker()
        for ticker in ["AAPL", "GOOG", "MSFT", "KO"]:
            response = self.client.post('/api/modify/follow',
                                        headers = {"Content-Type": "application/json"},
                                        json={'ticker': ticker}, follow_redirects=False)
            self.assertEqual(response.status_code, 200)
            self.assertEqual({'status': 'unfollowed', 'ticker': ticker}, response.json)

    def test_get_companies_incorrect_method(self):
        response = self.client.post('/api/get/companies', follow_redirects=True)
        self.assertEqual(response.status_code, 405)
        self.assertIn(b"Method Not Allowed", response.data)

    def test_get_companies_valid(self):
        response = self.client.get('/api/get/companies', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)
        for company in response.json:
            self.assertIsInstance(company, dict)
            self.assertIn('company_name', company)
            self.assertIn('stock_ticker', company)

    def test_get_articles_incorrect_method(self):
        response = self.client.post('/api/get/articles', follow_redirects=True)
        self.assertEqual(response.status_code, 405)
        self.assertIn(b"Method Not Allowed", response.data)

    def test_get_articles_no_args(self):
        response = self.client.get('/api/get/articles', follow_redirects=True)
        self.assertEqual(response.status_code, 400)
        self.assertEqual({'error': 'No tickers provided'}, response.json)
    
    def test_get_articles_no_tickers(self):
        response = self.client.get('/api/get/articles', follow_redirects=True,
                                    query_string={'tickers' : ""})

        self.assertEqual(response.status_code, 400)
        self.assertEqual({'error': 'No tickers provided'}, response.json)

    def test_get_articles_invalid_tickers(self):
        response = self.client.get('/api/get/articles', follow_redirects=True,
                                   query_string={'tickers' : "Apple,a,LONGSTRING,123,!£TI"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual({'articles': []}, response.json)


    def test_get_articles_with_ticker(self):
        def helper(tickers):
            response = self.client.get('/api/get/articles', follow_redirects=True,
                                        query_string={'tickers' : tickers})
            self.assertEqual(response.status_code, 200)
            self.assertIsInstance(response.json, dict)
            self.assertIn('articles', response.json)
            self.assertIsInstance(response.json['articles'], list)
            for article in response.json['articles']:
                self.assertIsInstance(article, dict)
                self.assertIn('ticker', article)
                self.assertIn('url', article)
                self.assertIn('source', article)
                self.assertIn('source_domain', article)
                self.assertIn('published', article)
                self.assertIn('description', article)
                self.assertIn('banner_image', article)
                self.assertIn('sentiment_label', article)
                self.assertIn('sentiment_score', article)
                self.assertIn('topics', article)
                self.assertIsInstance(article['topics'], list)
        
        helper("AAPL")
        helper("AAPL,GOOG")
        helper("AAPL,GOOG,MSFT,KO,JNJ,AMZN,PG")
    
    def test_get_notifs_incorrect_method(self):
        response = self.client.post('/api/get/notifications', follow_redirects=True)
        self.assertEqual(response.status_code, 405)
        self.assertIn(b"Method Not Allowed", response.data)
    
    def test_get_notifs(self):
        notif_count = 10
        for i in range(notif_count):
            notif = Notification(user_id=self.user.id, message=f'Test notification {i}')
            self.db.session.add(notif)
        self.db.session.commit()

        response = self.client.get('/api/get/notifications', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)
        self.assertEqual(len(response.json), notif_count)
        for notif in response.json:
            self.assertIsInstance(notif, dict)
            self.assertIn('message', notif)
            self.assertIn('time', notif)
            self.assertIn('id', notif)
    
    def test_delete_all_notif_incorrect_method(self):
        response = self.client.get('/api/delete/notifications', follow_redirects=True)
        self.assertEqual(response.status_code, 405)
        self.assertIn(b"Method Not Allowed", response.data)
        
    def add_notifications(self, notif_count):
        for i in range(notif_count):
            notif = Notification(user_id=self.user.id, message=f'Test notification {i}')
            self.db.session.add(notif)
        self.db.session.commit()
    
    def test_delete_all_notif(self):
        notif_count = 10
        self.add_notifications(notif_count)

        response = self.client.delete('/api/delete/notifications', follow_redirects=True)
        self.assertEqual(response.json,{'status': 'success'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Notification.query.filter_by(user_id=self.user.id).count(), 0)
    
    def test_delete_specific_notif_incorrect_method(self):
        response = self.client.get('/api/delete/notification/1', follow_redirects=True)
        self.assertEqual(response.status_code, 405)
        self.assertIn(b"Method Not Allowed", response.data)
    
    def test_delete_invalid_specific_notif(self):
        notif_count = 10
        self.add_notifications(notif_count)

        response = self.client.delete('/api/delete/notification/0', follow_redirects=True)
        self.assertEqual(response.json, {'status': 'error', 'message': 'Notification not found'})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(Notification.query.filter_by(user_id=self.user.id).count(), notif_count)

    def test_delete_valid_specific_notif(self):
        notif_count = 10
        self.add_notifications(notif_count)

        response = self.client.delete('/api/delete/notification/1', follow_redirects=True)
        self.assertEqual(response.json, {'status': 'success'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Notification.query.filter_by(user_id=self.user.id).count(), notif_count-1)