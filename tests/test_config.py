class TestConfig:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    TESTING = True
    SECURITY_PASSWORD_SALT = "f36d7eda6b91ecaff1a9e7045529ec71"
    SECRET_KEY = "123"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_USERNAME = 'donotreplysentify@gmail.com'
    MAIL_PASSWORD = 'uffc zybc kqga sebj'
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
