from functools import wraps
from google.appengine.ext import db
import app.keys.postkey as pkey

def does_post_exist(function):
    @wraps(function)
    def wrapper(self, post_id):
        if self.user:
            key = db.Key.from_path('Post', int(post_id), parent=pkey.post_key())
            post = db.get(key)
            if post:
                return function(self, post_id, post)
            else:
                self.error(404)
                return
        else:
            self.redirect('/login')
    return wrapper

def is_user(function):
    @wraps(function)
    def wrapper (self):
        if self.user:
            return function(self)
        else:
            self.error(404)
            return
    return wrapper


def does_user_own_post(function):
    @wraps(function)
    def wrapper (self, post_id):
        if self.user:
            key = db.Key.from_path('Post', int(post_id), parent=pkey.post_key())
            post = db.get(key)
            # user = User.by_name(self.user.name)
            if post and self.user.name == post.user.name:
                return function(self, post_id, post)
            else:
                self.redirect('/blog/')
                print post
                print user
                return
    return wrapper

def does_user_own_comment(function):
    @wraps(function)
    def wrapper(self, post_id, comment_id):
        if self.user:
            post_key = db.Key.from_path('Post', int(post_id))
            post = db.get(post_key)
            comment_key = db.Key.from_path('Comment', int(comment_id))
            comment = db.get(comment_key)
            if post_key and self.user.name == comment.user.name:
                return function(self, post_id, post, comment_id, comment)
            else:
                self.error(404)
                return
        else:
            self.redirect('/login')
            return
    return wrapper