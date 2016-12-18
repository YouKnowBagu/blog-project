from functools import wraps
from google.appengine.ext import db
import app.keys.postkey as pkey


def does_post_exist(function):
    @wraps(function)
    def wrapper(self, *args):
        print args
        arglist = list(args)
        results = []
        for i in arglist:
            results.append(i)
        print results
        post_id = results[0]
        key = db.Key.from_path('Post', int(post_id), parent=pkey.post_key())
        post = db.get(key)
        if post:
            results.append(post)
            print results
            return function(self, *results)
        else:
            self.error(404)
            return
    return wrapper

def does_comment_exist(function):
    @wraps(function)
    def wrapper(self, *args):
        arglist = []
        for i in args:
            arglist.append(i)
            post = arglist[2]
            comment_id = arglist[3]
        # postkey = db.Key.from_path('Post', int(post_id), parent=pkey.post_key())
        # post = db.get(postkey)
            key = db.Key.from_path('Comment', int(comment_id))
            comment = db.get(key)
            if post and comment:
                arglist[4] = comment
                return function(self, *arglist)
            else:
                self.error(404)
                return
    return wrapper

def is_user(function):
    @wraps(function)
    def wrapper (self, *args):
        print args
        arglist = list(args)
        results = []
        for i in arglist:
            results.append(i)
        user = self.user
        if user:
            results.append(user)
            print results
            return function(self, *results)
        else:
            redirerror = "You must be logged in to perform that action"
            self.redirect('/login', error = redirerror)
            return
    return wrapper

def does_user_own_post(function):
    @wraps(function)
    def wrapper (self, *args):
        arglist = list(args)
        print arglist
        results = []
        for i in arglist:
            results.append(i)
        post = results[1]
        if post and self.user.name == post.user.name:
            return function(self, *results)
        else:
            self.redirect('/blog/')
            return
    return wrapper

def does_user_own_comment(function):
    @wraps(function)
    def wrapper(self, *args):
        arglist = []
        for i in args:
            arglist.append(i)
        user = arglist[0]
        post = arglist[1]
        comment = arglist[2]
            # post_key = db.Key.from_path('Post', int(post_id))
            # post = db.get(post_key)
            # comment_key = db.Key.from_path('Comment', int(comment_id))
            # comment = db.get(comment_key)
        if post and comment and self.user.name == comment.user.name:
            return function(self, *arglist)
        else:
            self.redirect('/login')
    return wrapper