from google.appengine.ext import db

def user_key(name = 'default'):
    return db.Key.from_path('User', name)