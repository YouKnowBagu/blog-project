from google.appengine.ext import db
# from handlers import decorators, edit_comment, edit_post, frontpage, login, logout, newpost, permalink, signup
# from models import User, Post, Like, Unlike, Comment

def post_key(name = 'default'):
    return db.Key.from_path('Post', name)